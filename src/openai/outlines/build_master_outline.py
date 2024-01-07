from termcolor import colored
from openai import OpenAI
from src.utils.files import write_yaml_file, write_json_file
from src.utils.chat_helpers import slugify, get_prompt
import yaml


class MasterOutlineBuilder:
    def __init__(self, topic: str, client: OpenAI, output_path: str):
        # Initialize OpenAI
        topic_slug = slugify(topic)
        self.ai_client = client
        self.topic = topic
        self.topic_slug = topic_slug
        self.output_path = f"{output_path}/{topic_slug}"


    def build_optimize_outline_prompt(self, course_name: str, draft_outline: list[dict], modules: list[dict]) -> list[dict]:
        # Build message payload
        general_system_prompt = get_prompt('system/general', [("{topic}", self.topic)])
        chapters_system_prompt = get_prompt('system/tune-draft-outline', [
            ("{topic}", self.topic),
            ("{draft_outline}", yaml.dump(draft_outline))
        ])

        combined_system_prompt = "\n".join([
            general_system_prompt,
            chapters_system_prompt,
        ])

        user_prompt = get_prompt('user/chapters-outline', [
            ("{course_name}", course_name),
            ("{modules}", yaml.dump(modules))
        ])

        return [
            {"role": "system", "content": combined_system_prompt},
            {"role": "user", "content": user_prompt}
        ]


    def handle_course_optimize_response(self, content):
        yaml_content = content.split("yaml")[1].split("```")[0]
        data = yaml.safe_load(yaml_content)

        return {
            'dict': data,
            'yaml': yaml_content
        }


    def optimize_course_outline(self, course: dict, draft_outline: dict):
        course_name = course['courseName']
        modules = course['modules']

        print(colored(f"Generating {course_name} finalized outline...", "yellow"))

        course_name_formatted = slugify(course_name)
        save_file_name = f"outline-{course_name_formatted}"
        save_path = f"{self.output_path}/course-outlines"
        save_file_path = f"{save_path}/{save_file_name}.yaml"

        messages = self.build_optimize_outline_prompt(course_name, draft_outline['yaml'], modules)

        # Send to ChatGPT
        completion = self.ai_client.send_prompt('optimize-outline', messages)
        response_content = completion.choices[0].message.content
        print(colored("Done.", "green"))

        # Parse response
        parsed_response = self.handle_course_optimize_response(response_content)

        write_yaml_file(save_file_path, parsed_response['yaml'])
        return parsed_response



    def generate(self, draft_outline: dict):
        print(colored("\nBegin building master course outline...", "yellow"))
        master_outline = []

        for course in draft_outline['dict']:
            chapters = self.optimize_course_outline(course, draft_outline)
            course_object = {
                "courseName": course['courseName'],
                "chapters": chapters
            }
            master_outline.append(course_object)

        write_json_file(f"{self.output_path}/master-outline.json", master_outline)
        print(colored(f"Course outline finalized.", "green"))
        return master_outline
