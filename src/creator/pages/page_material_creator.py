import os
from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI
from src.creator.helpers import get_prompt
from src.creator.pages.page_summarizer import PageSummarizer
from db.db import DB, Topic, Page, Outline
import yaml
import progressbar


load_dotenv()


class PageMaterialCreator:
    def __init__(self, topic_id: int, client: OpenAI):
        self.topic = DB.get(Topic, topic_id)
        self.ai_client = client
        print(self.topic.master_outline_id)
        self.outline = DB.get(Outline, self.topic.master_outline_id)


    # Main


    def generate_page_material(self, page: Page):
        # Build prompt
        messages = self.build_page_material_prompt(page.name)

        # Send to ChatGPT
        validated_response = self.ai_client.send_prompt('page-material', messages, options={})
        material = validated_response['content']

        # Update page record
        page.content = material
        page.hash = Page.hash_page(material)
        page.link = page.permalink
        page.generated = True

        # Save to Database
        DB.commit()

        # Summarize Page
        summarizer = PageSummarizer(page, self.ai_client)
        summarizer.summarize()

        # Write to file
        page.dump_page()

        return page



    def create_from_outline(self):
        updated_pages = []
        page_entities = Outline.get_entities_by_type(DB, self.outline.id, 'Page')
        pages = [page for page in page_entities if page.type == 'page']  # Ignore challenges

        total_count = len(pages)

        with progressbar.ProgressBar(max_value=total_count, prefix='Generating pages: ', redirect_stdout=True).start() as bar:
            # Loop through outline pages
            for page in pages:
                existing = Page.check_for_existing_page_material(DB, page)
                if (existing):
                    print(colored(f"Skipping existing '{page.name}' page material...", "yellow"))
                    page.dump_page()  # Write to file
                    continue

                # Generate page material
                updated_page_record = self.generate_page_material(page)
                updated_pages.append(updated_page_record)

                bar.increment()

        return updated_pages



    # Prompts


    def collect_prior_page_summaries(self):
        summaries = ""

        # Fetch all pages from outline
        page_entities = Outline.get_entities_by_type(DB, self.outline.id, 'Page')
        lesson_pages = [page for page in page_entities if page.type == 'page']

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


    # Class Methods


    @classmethod
    def regenerate(self, client: OpenAI, topic: Topic, pages: list[Page]):
        lesson_pages = [page for page in pages if page.type == 'page']

        if len(lesson_pages) == 0:
            raise Exception(f"No lesson pages found for topic '{topic.name}'")

        page_creator = self(topic.id, client)

        regenerated_pages = []

        with progressbar.ProgressBar(max_value=len(lesson_pages), prefix='Regenerating pages: ', redirect_stdout=True).start() as bar:
            for page in lesson_pages:
                page.generated = False
                DB.add(page)

                regenerated = page_creator.generate_page_material(page)
                regenerated_pages.append(regenerated)

                bar.increment()

        return regenerated_pages
