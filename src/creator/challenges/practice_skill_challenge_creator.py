import os
from dotenv import load_dotenv
from openai import OpenAI
from termcolor import colored
from src.creator.helpers import get_prompt
from src.creator.outlines.outline_processor import OutlineProcessor
from src.creator.pages.page_processor import PageProcessor
from db.db import db_client, Topic, Page
import progressbar


load_dotenv()
DB = db_client()


class PracticeSkillChallengeCreator:
    def __init__(self, topic_name: str, client: OpenAI):
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'

        self.topic = DB.query(Topic).filter(Topic.name == topic_name).first()
        self.ai_client = client
        self.output_path = f"{output_directory}/{self.topic.slug}"
        self.outline = OutlineProcessor.get_or_create_outline_record_from_file(
            self.topic.id,
            f"{self.output_path}/master-outline.yaml"
        )


    def prepare_chapter_content_prompt(self, course_slug: str, chapter_slug: str):
        # Combine all page content into a single string
        chapter_pages_content = "The following is all the content from this chapter:\n\n"

        # Fetch all chapter pages
        chapter_pages = DB.query(Page).filter(
            Page.topic_id == self.topic.id,
            Page.course_slug == course_slug,
            Page.chapter_slug == chapter_slug
        ).all()

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

        user_prompt = get_prompt('user/practice-skill-challenge', None)

        # Build message payload
        system_payload = [{"role": "system", "content": combined_system_prompt}]
        user_payload = [{"role": "user", "content": user_prompt}]

        return system_payload + user_payload



    def generate_practice_skill_challenge(self, page: Page):
        # Build messages
        messages = self.build_skill_challenge_prompt(page.course_slug, page.chapter_slug)

        # Send to ChatGPT
        validated_response = self.ai_client.send_prompt('practice-skill-challenge', messages, options={})
        material = validated_response['content']

        # Update page record
        page.content = material
        page.hash = PageProcessor.hash_page(material)
        page.generated = True

        # Save to Database
        DB.add(page)
        DB.commit()

        return page


    def create_practice_skill_challenges(self):
        outline_rows = OutlineProcessor.get_outline_metadata(self.outline.id)
        challenge_pages = [row for row in outline_rows if row['type'] == 'challenge']
        total_count = len(challenge_pages)

        with progressbar.ProgressBar(max_value=total_count, prefix='Generating pages: ', redirect_stdout=True) as bar:
            # Loop through outline pages
            for row in challenge_pages:
                page_slug = row['slug']
                course_slug = row['courseSlug']
                chapter_slug = row['chapterSlug']

                existing = PageProcessor.check_for_existing_page_material(self.topic.id, row)   
                if (existing):
                    print(colored(f"Skipping existing '{row['name']}' page material...", "yellow"))
                    continue

                # Instantiate page record
                page_record = Page(
                    topic_id=self.topic.id,
                    name=row['name'],
                    course_slug=course_slug,
                    chapter_slug=chapter_slug,
                    slug=page_slug,
                    permalink=row['permalink'],
                    link=f"/page/{self.topic.slug}/{course_slug}/{chapter_slug}/{page_slug}",
                    type='challenge',
                    position=row['position'],
                    position_in_series=row['positionInSeries'],
                    position_in_course=row['positionInCourse'],
                    generated=False,
                    course_data=row['courseData'],
                )

                self.generate_practice_skill_challenge(page_record)

                bar.increment()
                
        return outline_rows
