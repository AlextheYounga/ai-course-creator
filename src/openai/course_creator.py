import os
from termcolor import colored
from openai import OpenAI
from .openai_handler import OpenAiHandler
from src.utils.files import read_json_file
from utils import reset_chat
from src.utils.chat_helpers import slugify
import json

class CourseCreator:
    def __init__(self, topic: str):
        # Initialize OpenAI
        topic_formatted = slugify(topic)
        self.ai_handler = OpenAiHandler()
        self.topic = topic
        self.topic_formatted = topic_formatted
        self.prompt_path = "src/data/prompts"
        self.creator_path = f"src/data/chat/creator/{topic_formatted}"


    def get_prompt(self, filename, replace: list[tuple]) -> str:
        prompt = open(f"{self.prompt_path}/{filename}.md", "r").read()

        if (replace != None):
            for item in replace:
                prompt = prompt.replace(item[0], item[1])

        return prompt


    def handle_json_prompt(self, messages: list[dict], retry=0):
        completion = self.ai_handler.send_prompt(messages)
        print(colored("Done.", "green"))

        # Parse outline
        response_content = completion.choices[0].message.content
        json_content = self.ai_handler.parse_markdown_json_list(response_content)

        # If JSON fails to parse, retry
        if (json_content == None):
            if (retry < 3):
                print(colored("Retrying...", "yellow"))
                retry += 1
                self.handle_json_prompt(messages, retry)
            else:
                print(colored("Failed to parse JSON.", "red"))
                return []

        return completion, json_content


    def generate_topic_skills(self):
        # Build message payload
        system_prompt = self.get_prompt('system/general', [("{topic}", self.topic)])
        user_prompt = self.get_prompt('user/topic-skills', [("{topic}", self.topic)])

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Send to ChatGPT and parse JSON
        print(colored(f"Generating {self.topic} skills...", "yellow"))
        completion, skills = self.handle_json_prompt(messages)

        # Save responses
        save_file_name = f"skills-{self.topic_formatted}"
        self._save_response_markdown_content(completion, self.creator_path, save_file_name)

        return skills

    def generate_series_outline(self, skills: list[dict]):
        # Build message payload
        system_prompt = self.get_prompt('system/skills-prep', [
            ("{topic}", self.topic),
            ("{skills}", json.dumps(skills))
        ])
        user_prompt = self.get_prompt('user/series-outline', [("{topic}", self.topic)])

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Send to ChatGPT and parse JSON
        print(colored(f"Generating {self.topic} series outline...", "yellow"))
        completion, outline = self.handle_json_prompt(messages)

        # Save responses
        save_file_name = f"series-{self.topic_formatted}"
        self._save_response_markdown_content(completion, self.creator_path, save_file_name)

        return outline

    def generate_course_chapters(self, course: dict, series: list[dict]):
        course_name = course['courseName']
        modules = course['modules']

        # Build message payload
        system_prompt = self.get_prompt('system/chapters-prep', [
            ("{topic}", self.topic),
            ("{series}", json.dumps(series))
        ])
        user_prompt = self.get_prompt('user/chapters-outline', [
            ("{course_name}", course_name),
            ("{modules}", json.dumps(modules))
        ])

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Send to ChatGPT and parse JSON
        print(colored(f"Generating {course_name} series chapters...", "yellow"))
        completion, chapters = self.handle_json_prompt(messages)

        # Save responses
        course_name_formatted = slugify(course_name)
        save_file_name = f"outline.md"
        save_path = f"{self.creator_path}/courses/{course_name_formatted}"
        self._save_response_markdown_content(completion, save_path, save_file_name)

        return chapters


    def generate_page_material(self, course_name, chapter: dict, page: str):
        # Build message payload
        system_prompt = self.get_prompt('system/page-material-prep', [
            ("{topic}", self.topic),
            ("{course_name}", course_name),
            ("{chapter}", json.dumps(chapter))
        ])
        user_prompt = self.get_prompt('user/page-material', [("{page_name}", page)])

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
        save_path = f"{self.creator_path}/courses/{course_name_formatted}/{chapter_name_formatted}"
        self._save_response_markdown_content(completion, save_path, save_file_name)

        return material


    def save_to_course_creator_path(self, save_file_name: str, data):
        save_file = f"{self.creator_path}/{save_file_name}.json"
        with open(save_file, 'w') as f:
            f.write(json.dumps(data))
            f.close()


    def _save_response_markdown_content(self, completion: OpenAI, save_path: str, save_file_name: str) -> None:
        # Check paths
        self._check_save_paths(save_path)

        # Save reply
        response_content = completion.choices[0].message.content
        with open(f"{save_path}/{save_file_name}.md", 'w') as f:
            f.write(response_content)
            f.close()


    def _check_save_paths(self, path):
        if not (os.path.exists(path)):
            os.makedirs(path, exist_ok=True)




def run():
    # Reset chat data folder before running
    reset_chat()

    try:
        topics = read_json_file("src/data/topics.json")

        # Generate series list of courses
        for topic in topics:
            creator = CourseCreator(topic)
            skills = creator.generate_topic_skills()
            series = creator.generate_series_outline(skills)

            final_course_outline = []
            print(colored(f"Begin optimizing course outline...", "yellow"))
            for course in series:
                chapters = creator.generate_course_chapters(course, series)
                course_object = {
                    "courseName": course['courseName'],
                    "chapters": chapters
                }
                final_course_outline.append(course_object)

            creator.save_to_course_creator_path("course-outline-final", final_course_outline)
            print(colored(f"Course outline finalized.", "green"))

            for course in final_course_outline:
                course_name = course['courseName']
                chapters = course['chapters']

                for chapter in chapters:
                    pages = chapter['pages']

                    for page in pages:
                        creator.generate_page_material(course_name, chapter, page)

        print(colored("Complete.", "green"))

    except KeyboardInterrupt:
        print(colored("Exiting...", "red"))


if __name__ == "__main__":
    run()
