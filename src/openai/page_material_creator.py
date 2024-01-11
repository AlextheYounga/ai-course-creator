import os
from termcolor import colored
from openai import OpenAI
from .openai_handler import OpenAiHandler
from src.utils.files import read_json_file, write_markdown_file
from src.utils.chat_helpers import slugify, get_prompt, copy_master_outline_to_yaml
import progressbar
import inquirer
import json


class PageMaterialCreator:
    def __init__(self, topic: str, client: OpenAI, output_path: str):
        topic_slug = slugify(topic)
        self.ai_client = client
        self.topic = topic
        self.topic_slug = topic_slug
        self.output_path = f"{output_path}/{topic_slug}"
        self.outline_path = f"{self.output_path}/master-outline.json"
        self.writing = False
        self.master_outline = {
            **self.get_master_outline(),
            'allPaths': []
        }

    def get_master_outline(self):
        if not os.path.exists(self.outline_path):
            raise Exception("Course outline not found.")

        try:
            return read_json_file(self.outline_path)
        except Exception as e:
            print(colored(f"Error reading course outline: {e}", "red"))
            return None


    def check_for_existing_material(self, course_slug: str, chapter_slug: str, page_slug: str):
        saved_material_file = f"{self.output_path}/content/{course_slug}/{chapter_slug}/page-{page_slug}.md"
        return os.path.exists(saved_material_file)


    def build_page_material_prompt(self, course_name, chapter: dict, page_name: str):
        # Combine multiple system prompts into one
        general_system_prompt = get_prompt('system/general', [("{topic}", self.topic)])
        interactives_system_prompt = get_prompt('system/tune-interactives', None)
        material_system_prompt = get_prompt('system/tune-page-material', [
            ("{topic}", self.topic),
            ("{course_name}", course_name),
            ("{chapter}", json.dumps(chapter))
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


    def update_master_outline(self, course_slug: str, chapter_slug: str, page_slug: str, save_path: str):
        # Update master outline
        page_path = f"{save_path}.md"

        self.master_outline['allPaths'].append(page_path)
        self.master_outline['courses'][course_slug]['paths'].append(page_path)
        self.master_outline['courses'][course_slug]['chapters'][chapter_slug]['paths'].append(page_path)
        self.master_outline['courses'][course_slug]['chapters'][chapter_slug]['pages'][page_slug]['path'] = page_path

        with open(self.outline_path, 'w') as json_file:
            json.dump(self.master_outline, json_file)


    def generate_page_material(self, course: dict, chapter: dict, page: dict):
        course_name = course['courseName']
        course_slug = course['slug']
        chapter_slug = chapter['slug']
        page_name = page['name']
        page_slug = page['slug']

        messages = self.build_page_material_prompt(course_name, chapter, page_name)

        # Send to ChatGPT
        validated_response = self.ai_client.send_prompt('page-material', messages, options={})
        material = validated_response['content']
        print(colored("Done.", "green"))

        # Save responses
        save_file_name = f"page-{page_slug}"
        save_path = f"{self.output_path}/content/{course_slug}/{chapter_slug}/{save_file_name}"
        write_markdown_file(save_path, material)

        # Update master outline with new page
        self.update_master_outline(course_slug, chapter_slug, page_slug, save_path)

        return material


    def create_pages_from_outline(self):
        total_count = self.master_outline['totalPages']
        with progressbar.ProgressBar(max_value=total_count, prefix='Generating pages: ', redirect_stdout=True) as bar:
            for course_slug, course_data in self.master_outline['courses'].items():
                chapters = course_data['chapters']

                for chapter_slug, chapter_data in chapters.items():
                    pages = chapter_data['pages']

                    for page_slug, page_data in pages.items():
                        page_name = page_data['name']
                        existing = self.check_for_existing_material(course_slug, chapter_slug, page_slug)

                        bar.increment()

                        if (existing):
                            print(colored(f"Skipping existing '{page_name}' page material...", "yellow"))
                            continue

                        self.generate_page_material(course_data, chapter_data, page_data)
        
        copy_master_outline_to_yaml(self.outline_path, self.master_outline)
        return self.master_outline



def main(topics: list[str]):
    # Generate series list of courses
    course_material_path = f"out/course_material"

    for topic in topics:
        print(colored(f"Begin generating {topic} page material...", "yellow"))

        # Initialize OpenAI
        session_name = f"{topic} Page Material"
        ai_client = OpenAiHandler(session_name)

        creator = PageMaterialCreator(topic, ai_client, course_material_path)
        creator.create_pages_from_outline()

    print(colored("Complete.\n", "green"))


def cli_prompt_user():
    try:
        topics = read_json_file("data/topics.json")
        topic_choices = ['All'] + topics

        choices = [
            inquirer.List('topic',
                          message="Which topic would you like to generate pages for?",
                          choices=topic_choices),
        ]

        choice = inquirer.prompt(choices)
        if choice != None:
            answer = choice['topic']

            if answer == 'All':
                main(topics)
            else:
                main([answer])

    except KeyboardInterrupt:
        print(colored("Exiting...", "red"))


if __name__ == "__main__":
    cli_prompt_user()
