import os
from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI
from src.creator.helpers import get_prompt
from src.creator.outlines.outline_processor import OutlineProcessor
from src.creator.pages.page_processor import PageProcessor
from db.db import db_client, Topic, Page
import progressbar


load_dotenv()
DB = db_client()


class PageMaterialCreator:
    def __init__(self, topic_name: str, client: OpenAI):
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'
        
        self.topic = DB.query(Topic).filter(Topic.name == topic_name).first()
        self.ai_client = client
        self.output_path = f"{output_directory}/{self.topic.slug}"
        self.outline = OutlineProcessor.get_or_create_outline_record_from_file(
            self.topic.id,
            f"{self.output_path}/master-outline.yaml"
        )


    def build_page_material_prompt(self, course_name, chapter_outline: str, page_name: str):
        # Combine multiple system prompts into one
        general_system_prompt = get_prompt('system/general', [("{topic}", self.topic.name)])
        interactives_system_prompt = get_prompt('system/tune-interactives', None)
        material_system_prompt = get_prompt('system/tune-page-material', [
            ("{topic}", self.topic.name),
            ("{course_name}", course_name),
            ("{chapter}", chapter_outline)
        ])

        combined_system_prompt = "\n".join([
            general_system_prompt,
            interactives_system_prompt,
            material_system_prompt
        ])

        user_prompt = get_prompt('user/page-material', [("{page_name}", page_name)])

        # Build message payload
        return [
            {"role": "system", "content": combined_system_prompt},
            {"role": "user", "content": user_prompt}
        ]


    def generate_page_material(self, page: Page):
        course_name = page.course_data['course']['name']
        chapter_outline = page.course_data['chapter']['outline']

        # Build prompt
        messages = self.build_page_material_prompt(course_name, chapter_outline, page.name)

        # Send to ChatGPT
        validated_response = self.ai_client.send_prompt('page-material', messages, options={})
        material = validated_response['content']

        # Update page record
        page.content = material
        page.hash = PageProcessor.hash_page(material)
        page.generated = True

        # Save to Database
        DB.add(page)
        DB.commit()

        return page


    def create_pages_from_outline(self):
        outline_rows = OutlineProcessor.get_outline_metadata(self.outline.id)
        pages = [row for row in outline_rows if row['type'] == 'page'] # Ignore challenges
        total_count = len(pages)

        with progressbar.ProgressBar(max_value=total_count, prefix='Generating pages: ', redirect_stdout=True) as bar:
            # Loop through outline pages
            for row in pages:
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
                    type='page',
                    position=row['position'],
                    position_in_series=row['positionInSeries'],
                    position_in_course=row['positionInCourse'],
                    generated=False,
                    course_data=row['courseData'],
                )

                self.generate_page_material(page_record)
                bar.increment()

        OutlineProcessor.dump_pages_from_outline(self.outline.id)

        return outline_rows
    






            


