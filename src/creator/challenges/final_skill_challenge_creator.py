
import os
from openai import OpenAI
from dotenv import load_dotenv
from termcolor import colored
from src.creator.helpers import get_prompt
from db.db import DB, Topic, Course, Page, Outline, OutlineEntity
from sqlalchemy.orm.attributes import flag_modified
from src.utils.chunks import chunks
import re
import markdown
from bs4 import BeautifulSoup
import progressbar


load_dotenv()


class FinalSkillChallengeCreator:
    def __init__(self, topic_id: int, client: OpenAI):
        self.topic = DB.get(Topic, topic_id)
        self.ai_client = client
        self.outline = Outline.get_master_outline(DB, self.topic)


    # Main


    def generate_final_skill_challenge(self, page: Page):
        messages = self.build_skill_challenge_prompt(page.course_slug)

        # Send to ChatGPT
        validated_response = self.ai_client.send_prompt('final-skill-challenge', messages, options={})
        material = validated_response['content']

        # Update page record
        page.content = material
        page.hash = Page.hash_page(material)
        page.link = page.permalink
        page.generated = True

        # Save to Database
        DB.commit()

        # Write to file
        page.dump_page()

        return page


    def create_from_outline(self):
        generated_pages = []
        entities = Outline.get_entities(DB, self.outline.id)
        fsc_pages = [page for page in entities['pages'] if page.type == 'final-skill-challenge']
        total_count = len(fsc_pages)

        with progressbar.ProgressBar(max_value=total_count, prefix='Generating final skill challenges: ', redirect_stdout=True).start() as bar:
            for page in fsc_pages:
                existing = Page.check_for_existing_page_material(DB, page)
                if (existing):
                    print(colored(f"Skipping existing '{page.name}' page material...", "yellow"))
                    page.dump_page()  # Write to file
                    bar.increment()
                    continue

                course_incomplete = self._check_course_incomplete(page.course_slug, entities['pages'])
                if course_incomplete:
                    print(colored(f"Skipping incomplete course '{page.course_slug}'...", "yellow"))
                    bar.increment()
                    continue

                page = self.generate_final_skill_challenge(page)
                generated_pages.append(page)

                bar.increment()

        return generated_pages


    # Prompts


    def prepare_course_content_prompt(self, course_slug: str):
        # Combine all page content into a single string
        course_pages_content = "The following is all the content from this course:\n\n"

        # Fetch all chapter pages
        pages = DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.outline.id,
            OutlineEntity.entity_type == "Page",
            Page.course_slug == course_slug,
            Page.type == 'page'
        ).all()

        for page in pages:
            course_pages_content += f"{page.content}\n\n"

        return course_pages_content


    def build_skill_challenge_prompt(self, course_slug: str):
        topic_language = self.topic.properties.get("language", self.topic.slug)

        # Combine all page content into a single string
        all_pages_content = self.prepare_course_content_prompt(course_slug)
        general_system_prompt = get_prompt(self.topic, 'system/general', [("{topic}", self.topic.name)])
        interactives_system_prompt = get_prompt(self.topic, 'system/tune-interactives', [("{topicLanguage}"), topic_language])

        combined_system_prompt = "\n".join([
            general_system_prompt,
            interactives_system_prompt,
            all_pages_content
        ])

        user_prompt = get_prompt(self.topic, 'user/challenges/final-skill-challenge', None)

        # Build message payload
        system_payload = [{"role": "system", "content": combined_system_prompt}]
        user_payload = [{"role": "user", "content": user_prompt}]

        return system_payload + user_payload



    # Class Methods


    @classmethod
    def regenerate(self, client: OpenAI, topic: Topic, course: Course):
        DB.query(Page).filter(
            Page.topic_id == course.topic_id,
            Page.course_slug == course.slug,
            Page.type == 'final-skill-challenge'
        ).delete()

        DB.commit()

        challenge_creator = self(topic.id, client)
        return challenge_creator.generate_final_skill_challenge(course)


    # Private Methods


    def _check_course_incomplete(self, course_slug: str, pages: list[Page]):
        pages_generated = [page.generated for page in pages if page.type == 'page' and page.course_slug == course_slug]
        return False in pages_generated
