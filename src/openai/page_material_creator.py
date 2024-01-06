import os
from termcolor import colored
from .openai_handler import OpenAiHandler
from src.utils.files import read_json_file, write_markdown_file
from src.utils.chat_helpers import slugify, get_prompt
import inquirer
import json
import shutil


class PageMaterialCreator:
    def __init__(self, topic: str):
        # Initialize OpenAI
        topic_formatted = slugify(topic)
        session_name = f"{topic} Page Material"
        self.ai_handler = OpenAiHandler(session_name)
        self.topic = topic
        self.topic_formatted = topic_formatted
        self.course_material_path = f"src/data/chat/course_material/{topic_formatted}"
        self.outline_path = f"{self.course_material_path}/master-outline.json"


    def setup(self):
        # Nuke content if it exists
        if os.path.exists(f"{self.course_material_path}/content"):
            shutil.rmtree(f"{self.course_material_path}/content")


    def get_course_outline(self):
        if not os.path.exists(self.outline_path):
            raise Exception("Course outline not found.")

        try:
            return read_json_file(self.outline_path)
        except Exception as e:
            print(colored(f"Error reading course outline: {e}", "red"))
            return None


    def check_for_existing_material(self, course_name, chapter: dict, page: str):
        course_name_formatted = slugify(course_name)
        chapter_name_formatted = slugify(chapter['chapterName'])
        page_name_formatted = slugify(page)

        saved_material_file = f"{self.course_material_path}/content/{course_name_formatted}/{chapter_name_formatted}/page-{page_name_formatted}.md"
        return os.path.exists(saved_material_file)


    def build_page_material_prompt(self, course_name, chapter: dict, page: str):
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

        user_prompt = get_prompt('user/page-material', [("{page_name}", page)])

        # Build message payload
        return [
            {"role": "system", "content": combined_system_prompt},
            {"role": "user", "content": user_prompt}
        ]


    def create_pages_from_outline(self, outline):
        for course in outline:
            course_name = course['courseName']
            chapters = course['chapters']

            for chapter in chapters:
                pages = chapter['pages']

                for page in pages:
                    existing = self.check_for_existing_material(course_name, chapter, page)
                    if (existing):
                        print(colored(f"Skipping existing '{page}' page material...", "yellow"))
                        continue

                    self.generate_page_material(course_name, chapter, page)


    def generate_page_material(self, course_name, chapter: dict, page: str):
        course_name_formatted = slugify(course_name)
        chapter_name_formatted = slugify(chapter['chapterName'])
        page_name_formatted = slugify(page)

        messages = self.build_page_material_prompt(course_name, chapter, page)

        # Send to ChatGPT
        print(colored(f"Generating '{page}' page material...", "yellow"))
        completion = self.ai_handler.send_prompt(messages)
        material = completion.choices[0].message.content
        print(colored("Done.", "green"))

        # Save responses
        save_file_name = f"page-{page_name_formatted}"
        save_path = f"{self.course_material_path}/content/{course_name_formatted}/{chapter_name_formatted}/{save_file_name}"
        write_markdown_file(save_path, material)

        return material




def _process_topics(topics: list[str]):
    topics = read_json_file("src/data/topics.json")

    # Generate series list of courses
    for topic in topics:
        print(colored(f"Begin generating {topic} page material...", "yellow"))

        creator = PageMaterialCreator(topic)
        creator.setup()
        outline = creator.get_course_outline()
        creator.create_pages_from_outline(outline)


    print(colored("Complete.", "green"))


def run_page_creator():
    try:
        topics = read_json_file("src/data/topics.json")
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
                _process_topics(topics)
            else:
                _process_topics([answer])

    except KeyboardInterrupt:
        print(colored("Exiting...", "red"))


if __name__ == "__main__":
    run_page_creator()
