import os
from termcolor import colored
from openai import OpenAI
from .openai_handler import OpenAiHandler
from src.utils.files import read_json_file
from datetime import datetime



class CourseCreator:
    def __init__(self):
        # Initialize OpenAI
        self.ai_handler = OpenAiHandler()
        self.prompt_path = f"src/data/prompts"
        self.payload_path = f"src/data/chat/payloads"
        self.creator_path = f"src/data/chat/creator"


    def get_prompt(self, filename, replace: list[tuple]) -> str:
        prompt = open(f"{self.prompt_path}/{filename}.md", "r").read()

        if (replace != None):
            for item in replace:
                prompt = prompt.replace(item[0], item[1])

        return prompt


    def generate_series(self, topic, retry=0):
        # Build message payload
        system_prompt = self.get_prompt('system', [("{course_name}", topic)])
        series_prompt = self.get_prompt('series', [("{course_name}", topic)])

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": series_prompt}
        ]

        # Send to ChatGPT
        print(colored(f"Generating {topic} series...", "yellow"))
        completion = self.ai_handler.send_prompt(messages)
        print(colored("Done.", "green"))

        # Save responses
        formatted_name = topic.lower().replace(" ", "-")
        save_file_name = "series-" + formatted_name
        self.creator_path = f"{self.creator_path}/{formatted_name}" if retry == 0 else self.creator_path
        self.save_responses(completion, self.creator_path, save_file_name)

        # Parse outline
        response_content = completion.choices[0].message.content
        series_json = self.ai_handler.parse_markdown_json(response_content)

        # If JSON fails to parse, retry
        if (series_json == None):
            if (retry < 3):
                print(colored("Retrying...", "yellow"))
                retry += 1
                self.generate_series(topic, retry)
            else:
                print(colored("Failed to generate series.", "red"))
                return []

        return series_json


    def generate_outline(self, topic, course_name, retry=0):
        # Build message payload
        system_prompt = self.get_prompt('system', [("{course_name}", topic)])
        outline_prompt = self.get_prompt('outline', [("{course_name}", course_name)])
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": outline_prompt}
        ]

        # Send to ChatGPT
        print(colored(f"Generating {course_name} outline...", "yellow"))
        completion = self.ai_handler.send_prompt(messages)
        print(colored("Done.", "green"))

        # Save responses
        formatted_course_name = course_name.lower().replace(" ", "-")
        save_file_name = "outline-" + formatted_course_name
        response_path = f"{self.creator_path}/{formatted_course_name}"
        self.save_responses(completion, response_path, save_file_name)

        # Parse outline
        response_content = completion.choices[0].message.content
        outline_json = self.ai_handler.parse_markdown_json(response_content)

        # If JSON fails to parse, retry
        if (outline_json == None):
            if (retry < 3):
                print(colored("Retrying...", "yellow"))
                retry += 1
                self.generate_outline(topic, course_name, retry)
            else:
                print(colored("Failed to generate outline.", "red"))
                return []

        return outline_json


    def generate_page_material(self, topic, course_name, page):
        # Build message payload
        system_prompt = self.get_prompt('system', [("{course_name}", topic)])
        page_material_prompt = self.get_prompt('page_material', [("{page_name}", page)])
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": page_material_prompt}
        ]

        # Send to ChatGPT
        print(colored(f"Generating {page} material...", "yellow"))
        completion = self.ai_handler.send_prompt(messages)
        print(colored("Done.", "green"))

        formatted_course_name = course_name.lower().replace(" ", "-")
        formatted_page_name = page.lower().replace(" ", "-")
        save_file_name = "page-" + formatted_page_name
        response_path = f"{self.creator_path}/{formatted_course_name}"
        self.save_responses(completion, response_path, save_file_name)

        response_content = completion.choices[0].message.content

        return response_content


    def save_responses(self, completion: OpenAI, save_path: str, save_file_name: str) -> None:
        # Check paths
        storage_file = f"{save_path}/{save_file_name}.md"

        self.check_save_paths(self.payload_path)
        self.check_save_paths(save_path)

        # Save payload log
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        payload_file = f"{self.payload_path}/{save_file_name}-{timestamp}.json"
        with open(payload_file, 'w') as f:
            f.write(completion.model_dump_json())
            f.close()

        # Save reply
        response_content = completion.choices[0].message.content
        with open(storage_file, 'w') as f:
            f.write(response_content)
            f.close()


    def check_save_paths(self, path):
        if not (os.path.exists(path)):
            os.mkdir(path)




def run():
    try:
        topics = read_json_file("src/data/topics.json")

        # Generate series list of courses
        for topic in topics:
            creator = CourseCreator()
            series = creator.generate_series(topic)

            # Generate course outline
            for course in series:
                outline = creator.generate_outline(topic, course)

                # Generate page material
                for item in outline:
                    # TODO: Add a chapter introduction page
                    chapter = item['chapterName']
                    pages = item['pages']

                    for page in pages:
                        creator.generate_page_material(topic, course, page)
        print(colored("Done.", "green"))

    except KeyboardInterrupt:
        print(colored("Exiting...", "red"))


if __name__ == "__main__":
    run()
