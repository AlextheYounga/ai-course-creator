
import os
from openai import OpenAI
from dotenv import load_dotenv
from termcolor import colored
from src.creator.helpers import get_prompt
from db.db import DB, Topic, Course, Chapter, Page, Outline
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
        self.outline = Outline.process_outline(DB, self.topic.id)


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

        with progressbar.ProgressBar(max_value=courses_count, prefix='Generating final skill challenges: ', redirect_stdout=True).start() as bar:
            for course in courses:
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

                bar.increment()

        return generated_pages


    # Prompts


    def prepare_course_content_prompt(self, course_slug: str):
        # Combine all page content into a single string
        course_pages_content = "The following is all the content from this course:\n\n"

        # Fetch all chapter pages
        page_entities = Outline.get_entities_by_type(DB, self.outline.id, 'Page')
        pages = [
            page for page in page_entities
            if page.type == 'page' and page.course_slug == course_slug
        ]

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
        ).count()

        return fsc_pages > 0


    def _check_course_incomplete(self, pages: list[Page]):
        pages_generated = [page.generated for page in pages if page.type == 'page']
        return False in pages_generated


    def _handle_allocate_page_material_to_multiple_pages(self, course: Course, material: str):
        # Parse response for answerables
        answerables = self._handle_split_page_material(material)
        fsc_chapter_slug = course.skill_challenge_chapter

        generated_pages = []
        for index, page_material in enumerate(answerables):
            page = self._create_fsc_page_record(course, fsc_chapter_slug, index, page_material)
            generated_pages.append(page)

        return generated_pages


    def _create_fsc_page_record(self, course: Course, fsc_chapter_slug: str, page_index: int, page_material: str):
        page_count = DB.query(Page).filter(
            Page.topic_id == self.topic.id,
            Page.course_slug == course.slug,
        ).count()

        chapter = DB.query(Chapter).filter(
            Chapter.topic_id == self.topic.id,
            Chapter.course_slug == course.slug,
            Chapter.slug == fsc_chapter_slug
        ).first()

        if not chapter:
            self._create_fsc_chapter(course, fsc_chapter_slug)

        page_name = f"Final Skill Challenge Page {page_index + 1}"
        page = Page.first_or_create(
            DB,
            self.topic,
            {
                'name': page_name,
                'outlineName': self.outline.name,
                'courseSlug': course.slug,
                'chapterSlug': fsc_chapter_slug,
                'position': page_index,
                'positionInCourse': page_count + 1,
                'content': page_material
            })

        page.generated = True

        # Save to Database
        DB.add(page)
        DB.commit()

        # Write to file
        page.dump_page()

        return page


    def _create_fsc_chapter(self, course: Course, fsc_chapter_slug: str):
        chapter_count = DB.query(Chapter).filter(
            Chapter.topic_id == self.topic.id,
            Chapter.course_slug == course.slug,
        ).count()

        chapter = Chapter.first_or_create(
            DB,
            self.topic,
            {
                'name': fsc_chapter_slug,
                'courseSlug': course.slug,
                'position': chapter_count + 1,
            })

        DB.add(chapter)
        DB.commit()


    def _handle_split_page_material(self, material: str) -> list:
        # Split 20 questions into chunks of 4 questions per page
        html = markdown.markdown(material, extensions=['fenced_code'])
        soup = BeautifulSoup(html, 'html.parser')

        answerables = soup.findAll("div", {"id": re.compile('answerable-*')})
        question_count = len(answerables)
        optimal_divisor = self._find_optimal_divisor(question_count)
        answerable_chunks = chunks(answerables, optimal_divisor)

        answerables_for_pages = []
        for chunk in answerable_chunks:
            text_chunks = [str(item) for item in chunk]
            rejoined_answerables = ("\n\n").join(text_chunks)
            answerables_for_pages.append(rejoined_answerables)

        return answerables_for_pages


    def _find_optimal_divisor(self, question_count: int):
        # Find the optimal divisor for the number of questions
        optimal_divisor = 0
        for i in range(4, 9):
            if question_count % i == 0:
                optimal_divisor = i

        if optimal_divisor == 0:
            optimal_divisor = 5

        return optimal_divisor
