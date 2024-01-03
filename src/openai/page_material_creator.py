import os
from termcolor import colored
from openai import OpenAI
from .openai_handler import OpenAiHandler
from src.utils.files import read_json_file
from utils import reset_chat
from src.utils.chat_helpers import slugify, get_prompt
import json


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


    def read_course_outline(self):
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


    def generate_page_material(self, course_name, chapter: dict, page: str):
        # Build message payload
        system_prompt = get_prompt('system/page-material-prep', [
            ("{topic}", self.topic),
            ("{course_name}", course_name),
            ("{chapter}", json.dumps(chapter))
        ])
        user_prompt = get_prompt('user/page-material', [("{page_name}", page)])

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        course_name_formatted = slugify(course_name)
        chapter_name_formatted = slugify(chapter['chapterName'])
        page_name_formatted = slugify(page)

        # Send to ChatGPT
        print(colored(f"Generating '{page}' page material...", "yellow"))
        completion = self.ai_handler.send_prompt(messages)
        material = completion.choices[0].message.content
        print(colored("Done.", "green"))

        # Save responses
        save_file_name = f"page-{page_name_formatted}"
        save_path = f"{self.course_material_path}/content/{course_name_formatted}/{chapter_name_formatted}"
        self.ai_handler.save_response_markdown(completion, save_path, save_file_name)

        return material




def run_page_creator():
    try:
        topics = read_json_file("src/data/topics.json")

        # Generate series list of courses
        for topic in topics:
            print(colored(f"Begin generating {topic} page material...", "yellow"))

            creator = PageMaterialCreator(topic)
            outline = creator.read_course_outline()

            for course in outline:
                course_name = course['courseName']
                chapters = course['chapters']

                for chapter in chapters:
                    pages = chapter['pages']

                    for page in pages:
                        existing = creator.check_for_existing_material(course_name, chapter, page)
                        if (existing):
                            print(colored(f"Skipping existing '{page}' page material...", "yellow"))
                            continue

                        creator.generate_page_material(course_name, chapter, page)

        print(colored("Complete.", "green"))

    except KeyboardInterrupt:
        print(colored("Exiting...", "red"))


if __name__ == "__main__":
    run_page_creator()
