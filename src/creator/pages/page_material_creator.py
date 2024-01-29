import os
from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI
from src.creator.helpers import get_prompt
from src.creator.outlines.outline_processor import OutlineProcessor
from src.creator.pages.page_processor import PageProcessor
from src.creator.pages.page_summarizer import PageSummarizer
from db.db import DB, Topic, Page
import yaml
import progressbar


load_dotenv()


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


    def collect_prior_page_summaries(self):
        summaries = ""

        # Fetch all pages from outline
        outline_records = OutlineProcessor.get_outline_record_ids(self.outline.id)
        page_ids = outline_records['pages']
        outline_pages = DB.query(Page).filter(Page.id.in_(page_ids)).all()
        lesson_pages = [page for page in outline_pages if page.type == 'page']

        for page in lesson_pages:
            if page.type == 'page' and page.summary != None:
                formatted_summary = page.summary.replace("\n", " ")
                summaries += f"## {page.name}\n {formatted_summary}\n\n"

        return summaries


    def format_outline_for_prompt(self):
        outline_formatted = []

        for course in self.outline.master_outline:
            course_object = {
                'course': {
                    'courseName': course['course']['courseName'],
                    'chapters': []
                }
            }

            chapters = course['course']['chapters']
            pruned_chapters = [chapter for chapter in chapters if chapter['name'] != 'Final Skill Challenge']
            course_object['course']['chapters'] = pruned_chapters

            for index, chapter in enumerate(course_object['course']['chapters']):
                pages = chapter['pages']
                pruned_pages = [page for page in pages if page != 'Practice Skill Challenge']
                course_object['course']['chapters'][index]['pages'] = pruned_pages

            outline_formatted.append(course_object)
        return outline_formatted


    def build_page_material_prompt(self, page_name: str):
        # Combine multiple system prompts into one
        general_system_prompt = get_prompt('system/general', [("{topic}", self.topic.name)])

        # Inform model on how we want to format interactives
        interactives_system_prompt = get_prompt('system/tune-interactives', None)

        # Inform model on our outline
        outline_formatted = self.format_outline_for_prompt()
        material_system_prompt = get_prompt('system/pages/tune-outline', [
            ("{topic}", self.topic.name),
            ("{outline}", yaml.dump(outline_formatted, sort_keys=False)),
        ])

        # Get prior page summaries
        summaries = self.collect_prior_page_summaries()

        prior_page_material_prompt = get_prompt(
            'system/pages/tune-page-summaries',
            [("{summaries}", summaries)]
        )

        combined_system_prompt = "\n---\n".join([
            general_system_prompt,
            interactives_system_prompt,
            material_system_prompt,
            prior_page_material_prompt
        ])

        user_prompt = get_prompt('user/pages/page-material', [("{page_name}", page_name)])

        # Build message payload
        return [
            {"role": "system", "content": combined_system_prompt},
            {"role": "user", "content": user_prompt}
        ]


    def generate_page_material(self, page: Page):
        # Build prompt
        messages = self.build_page_material_prompt(page.name)

        # Send to ChatGPT
        validated_response = self.ai_client.send_prompt('page-material', messages, options={})
        material = validated_response['content']

        # Update page record
        page.content = material
        page.hash = PageProcessor.hash_page(material)
        page.link = page.permalink
        page.generated = True

        # Save to Database
        DB.commit()

        # Summarize Page
        summarizer = PageSummarizer(page, self.ai_client)
        summarizer.summarize()

        # Write to file
        PageProcessor.dump_page(page)

        return page


    def regenerate(self, pages: list[Page]):
        regenerated_pages = []

        with progressbar.ProgressBar(max_value=len(pages), prefix='Regenerating pages: ', redirect_stdout=True) as bar:
            for page in pages:
                page.generated = False
                DB.add(page)

                regenerated = self.generate_page_material(page)
                regenerated_pages.append(regenerated)

            bar.increment()

        return regenerated_pages


    def create_from_outline(self):
        updated_pages = []
        outline_records = OutlineProcessor.get_outline_records(self.outline.id)
        pages = [page for page in outline_records if page.type == 'page']  # Ignore challenges

        total_count = len(pages)

        with progressbar.ProgressBar(max_value=total_count, prefix='Generating pages: ', redirect_stdout=True) as bar:
            # Loop through outline pages
            for page in pages:
                bar.increment()

                existing = PageProcessor.check_for_existing_page_material(page)
                if (existing):
                    print(colored(f"Skipping existing '{page.name}' page material...", "yellow"))
                    PageProcessor.dump_page(page)  # Write to file
                    continue

                updated_page_record = self.generate_page_material(page)
                updated_pages.append(updated_page_record)



        return updated_pages
