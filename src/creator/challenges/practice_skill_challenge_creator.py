import os
from dotenv import load_dotenv
from openai import OpenAI
from termcolor import colored
from src.creator.helpers import get_prompt
from db.db import DB, Topic, Page, Outline
import progressbar


load_dotenv()


class PracticeSkillChallengeCreator:
    def __init__(self, topic_id: int, client: OpenAI):
        self.topic = DB.get(Topic, topic_id)
        self.ai_client = client
        self.outline = Outline.get_master_outline(DB, self.topic)


    # Main


    def generate_practice_skill_challenge(self, page: Page):
        # Build messages
        messages = self.build_skill_challenge_prompt(page.course_slug, page.chapter_slug)

        # Send to ChatGPT
        validated_response = self.ai_client.send_prompt('practice-skill-challenge', messages, options={})
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
        updated_pages = []
        page_entities = Outline.get_entities_by_type(DB, self.outline.id, 'Page')
        challenge_pages = [page for page in page_entities if page.type == 'challenge']
        total_count = len(challenge_pages)

        with progressbar.ProgressBar(max_value=total_count, prefix='Generating practice challenges: ', redirect_stdout=True).start() as bar:
            # Loop through outline pages
            for page in challenge_pages:
                existing = Page.check_for_existing_page_material(DB, page)
                if (existing):
                    print(colored(f"Skipping existing '{page.name}' page material...", "yellow"))
                    page.dump_page()  # Write to file
                    bar.increment()
                    continue


                chapter_incomplete = self._check_chapter_incomplete(page_entities, page)
                if chapter_incomplete:
                    print(colored(f"Skipping incomplete chapter {page.chapter_slug}...", "yellow"))
                    bar.increment()
                    continue

                updated_page_record = self.generate_practice_skill_challenge(page)
                updated_pages.append(updated_page_record)
                bar.increment()

        return updated_pages


    # Prompts


    def prepare_chapter_content_prompt(self, course_slug: str, chapter_slug: str):
        # Combine all page content into a single string
        chapter_pages_content = "The following is all the content from this chapter:\n\n"

        # Fetch all chapter pages
        page_entities = Outline.get_entities_by_type(DB, self.outline.id, 'Page')
        chapter_pages = [
            page for page in page_entities
            if page.type == 'page' and page.course_slug == course_slug and page.chapter_slug == chapter_slug
        ]

        for page in chapter_pages:
            if page.content != None:
                chapter_pages_content += f"{page.content}\n\n"

        return chapter_pages_content


    def build_skill_challenge_prompt(self, course_slug: str, chapter_slug: str):
        # Combine all page content into a single string
        all_pages_content = self.prepare_chapter_content_prompt(course_slug, chapter_slug)

        general_system_prompt = get_prompt('system/general', [("{topic}", self.topic.name)])
        interactives_system_prompt = get_prompt('system/tune-interactives', None)

        combined_system_prompt = "\n".join([
            general_system_prompt,
            interactives_system_prompt,
            all_pages_content
        ])

        user_prompt = get_prompt('user/challenges/practice-skill-challenge', None)

        # Build message payload
        system_payload = [{"role": "system", "content": combined_system_prompt}]
        user_payload = [{"role": "user", "content": user_prompt}]

        return system_payload + user_payload


    # Class Methods


    @classmethod
    def regenerate(self, client: OpenAI, topic: Topic, pages: list[Page]):
        challenge_pages = [page for page in pages if page.type == 'challenge']

        if len(challenge_pages) == 0:
            raise Exception(f"No challenge pages found for topic '{topic.name}'")

        challenge_creator = self(topic.id, client)

        regenerated_pages = []

        with progressbar.ProgressBar(max_value=len(challenge_pages), prefix='Regenerating challenges: ', redirect_stdout=True).start() as bar:
            for page in challenge_pages:
                page.generated = False

                regenerated = challenge_creator.generate_practice_skill_challenge(page)
                regenerated_pages.append(regenerated)

                bar.increment()

        return regenerated_pages


    # Private Methods


    def _check_chapter_incomplete(self, page_entities: list[Page], challenge_page: Page):
        for page in page_entities:
            if page.chapter_slug == challenge_page.chapter_slug:
                if page.type == 'page' and page.generated == False:
                    return True

        return False
