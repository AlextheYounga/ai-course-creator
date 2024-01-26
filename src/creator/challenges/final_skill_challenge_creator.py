
import os
from openai import OpenAI
from dotenv import load_dotenv
from src.creator.helpers import get_prompt
from src.creator.outlines.outline_processor import OutlineProcessor
from src.creator.pages.page_processor import PageProcessor
from db.db import DB, Topic, Course, Page
from src.utils.chunks import chunks
import re
import markdown
from bs4 import BeautifulSoup
import progressbar


load_dotenv()


class FinalSkillChallengeCreator:
    def __init__(self, topic_name: str, client: OpenAI):
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'

        self.topic = DB.query(Topic).filter(Topic.name == topic_name).first()
        self.ai_client = client
        self.output_path = f"{output_directory}/{self.topic.slug}"
        self.outline = OutlineProcessor.get_or_create_outline_record_from_file(
            self.topic.id,
            f"{self.output_path}/master-outline.yaml"
        )


    def prepare_course_content_prompt(self, course_slug: str):
        # Combine all page content into a single string
        course_pages_content = "The following is all the content from this course:\n\n"

        pages = DB.query(Page).filter(
            Page.topic_id == self.topic.id,
            Page.course_slug == course_slug
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

        user_prompt = get_prompt('user/final-skill-challenge', None)

        # Build message payload
        system_payload = [{"role": "system", "content": combined_system_prompt}]
        user_payload = [{"role": "user", "content": user_prompt}]

        return system_payload + user_payload


    def generate_final_skill_challenge(self, course: Course):
        messages = self.build_skill_challenge_prompt(course.slug)

        # Send to ChatGPT
        validated_response = self.ai_client.send_prompt('final-skill-challenge', messages, options={})
        material = validated_response['content']

        generated_pages = self._handle_split_page_material(course, material)

        return generated_pages


    # Main
    def create_from_outline(self):
        generated_pages = []
        outline_records = OutlineProcessor.get_outline_record_ids(self.outline.id)
        course_ids = outline_records['courses']
        courses = DB.query(Course).filter(Course.id.in_(course_ids)).all()
        courses_count = len(courses)

        with progressbar.ProgressBar(max_value=courses_count, prefix='Generating final skill challenges: ', redirect_stdout=True) as bar:
            for course in courses:
                pages = self.generate_final_skill_challenge(course)
                generated_pages += pages
                bar.increment()

        OutlineProcessor.dump_pages_from_outline(self.outline.id)

        return generated_pages


    # Private Methods
    def _handle_split_page_material(self, course: Course, material: str):
        # Parse response for answerables
        answerables = self._parse_response_answerables(material)
        fsc_chapter = course.skill_challenge_chapter
        fsc_pages = DB.query(Page).filter(Page.topic_id == self.topic.id, Page.chapter_slug == fsc_chapter).all()

        generated_pages = []
        for index, page in enumerate(fsc_pages):
            page_material = answerables[index]

            # Update page record
            page.content = page_material
            page.hash = PageProcessor.hash_page(page_material)
            page.link = page.permalink
            page.generated = True

            # Save to Database
            DB.add(page)
            DB.commit()
            DB.refresh(page)

            generated_pages.append(page)
        
        return generated_pages


    def _parse_response_answerables(self, material: str) -> list:
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
