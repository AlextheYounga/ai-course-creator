
import os
from openai import OpenAI
from dotenv import load_dotenv
from termcolor import colored
from src.creator.helpers import get_prompt
from db.db import DB, Topic, Course, Page, Outline
from src.utils.chunks import chunks
from src.creator.content_parser import ContentParser
import re
import markdown
from bs4 import BeautifulSoup
import progressbar


load_dotenv()


class FinalSkillChallengeCreator:
    def __init__(self, topic_id: int, client: OpenAI):
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'

        self.topic = DB.get(Topic, topic_id)
        self.ai_client = client
        self.output_path = f"{output_directory}/{self.topic.slug}"
        self.outline = self.outline = Outline.process_outline(DB, self.topic.id, f"{self.output_path}/master-outline.yaml")


    # Main


    def generate_final_skill_challenge(self, course: Course):
        messages = self.build_skill_challenge_prompt(course.slug)

        # Send to ChatGPT
        validated_response = self.ai_client.send_prompt('final-skill-challenge', messages, options={})
        material = validated_response['content']

        generated_pages = self._handle_allocate_page_material_to_multiple_pages(course, material)

        return generated_pages


    def create_from_outline(self):
        generated_pages = []
        outline_records = Outline.get_entities(DB, self.outline.id)
        courses = outline_records['courses']
        courses_count = len(courses)

        with progressbar.ProgressBar(max_value=courses_count, prefix='Generating final skill challenges: ', redirect_stdout=True) as bar:
            for course in courses:
                bar.increment()

                existing = self._check_for_existing_page_material(course)
                if (existing):
                    print(colored(f"Skipping existing '{course.name}' final skill challenge material...", "yellow"))
                    continue

                course_incomplete = self._check_course_incomplete(outline_records['pages'])
                if course_incomplete:
                    print(colored(f"Skipping incomplete course '{course.name}'...", "yellow"))
                    continue

                pages = self.generate_final_skill_challenge(course)
                generated_pages += pages

        return generated_pages


    # Prompts


    def prepare_course_content_prompt(self, course_slug: str):
        # Combine all page content into a single string
        course_pages_content = "The following is all the content from this course:\n\n"

        pages = DB.query(Page).filter(
            Page.topic_id == self.topic.id,
            Page.course_slug == course_slug,
            Page.type == 'page'
        ).all()

        for page in pages:
            course_pages_content += f"{page.content}\n\n"

        return course_pages_content


    def build_skill_challenge_prompt(self, course_slug: str):
        # Combine all page content into a single string
        all_pages_content = self.prepare_course_content_prompt(course_slug)

        general_system_prompt = get_prompt('system/general', [("{topic}", self.topic.name)])
        interactives_system_prompt = get_prompt('system/tune-interactives', None)

        combined_system_prompt = "\n".join([
            general_system_prompt,
            interactives_system_prompt,
            all_pages_content
        ])

        user_prompt = get_prompt('user/challenges/final-skill-challenge', None)

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


    def _check_for_existing_page_material(self, course: Course):
        fsc_pages = DB.query(Page).filter(
            Page.topic_id == self.topic.id,
            Page.course_slug == course.slug,
            Page.type == 'final-skill-challenge'
        ).all()

        content_generated = [page.content != None for page in fsc_pages]

        if (False not in content_generated):
            Page.dump_pages(fsc_pages)  # Write to file
            return True

        return False


    def _check_course_incomplete(self, pages: list[Page]):
        pages_generated = [page.generated for page in pages if page.type == 'page']
        return False in pages_generated


    def _handle_allocate_page_material_to_multiple_pages(self, course: Course, material: str):
        # Parse response for answerables
        answerables = self._handle_split_page_material(material)
        fsc_chapter = course.skill_challenge_chapter
        fsc_pages = DB.query(Page).filter(Page.topic_id == self.topic.id, Page.chapter_slug == fsc_chapter).all()

        generated_pages = []
        for index, page in enumerate(fsc_pages):
            if index >= len(answerables): break

            page_material = answerables[index]
            page = self._update_fsc_page_record(page, page_material)
            generated_pages.append(page)

        return generated_pages


    def _update_fsc_page_record(self, page: Page, page_material: str):
        # Update page record
        page.content = page_material
        page.hash = Page.hash_page(page_material)
        page.link = page.permalink
        page.generated = True

        # Save to Database
        DB.add(page)
        DB.commit()
        DB.refresh(page)

        # Parse nodes from page material
        parser = ContentParser(page)
        page = parser.parse_nodes()

        # Write to file
        page.dump_page()

        return page



    def _handle_split_page_material(self, material: str) -> list:
        # Split 20 questions into chunks of 4 questions per page
        html = markdown.markdown(material, extensions=['fenced_code'])
        soup = BeautifulSoup(html, 'html.parser')

        answerables = soup.findAll("div", {"id": re.compile('answerable-*')})
        answerable_chunks = chunks(answerables, 4)

        answerables_for_pages = []
        for chunk in answerable_chunks:
            text_chunks = [str(item) for item in chunk]
            rejoined_answerables = ("\n\n").join(text_chunks)
            answerables_for_pages.append(rejoined_answerables)

        return answerables_for_pages
