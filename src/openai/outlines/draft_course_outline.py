from termcolor import colored
from openai import OpenAI
from src.utils.files import write_json_file
from src.utils.chat_helpers import slugify, get_prompt
import yaml


class OutlineDraft:
    def __init__(self, topic: str, client: OpenAI):
        # Initialize OpenAI
        topic_formatted = slugify(topic)
        self.ai_client = client
        self.topic = topic
        self.topic_formatted = topic_formatted
        self.course_material_path = f"src/data/chat/course_material/{topic_formatted}"
    

    def build_draft_prompt(self, skills: yaml) -> list[dict]:
        # Build message payload
        general_system_prompt = get_prompt('system/general', [("{topic}", self.topic)])
        skills_system_prompt = get_prompt('system/tune-skills', [
            ("{topic}", self.topic),
            ("{skills}", yaml.dump(skills))
        ])

        user_prompt = get_prompt('user/draft-outline', [("{topic}", self.topic)])

        combined_system_prompt = "\n".join([
            general_system_prompt,
            skills_system_prompt,
        ])

        return [
            {"role": "system", "content": combined_system_prompt},
            {"role": "user", "content": user_prompt}
        ]


    def handle_outline_draft_response(self, content: str):
        yaml_content = content.split("yaml")[1].split("```")[0]
        data = yaml.safe_load(yaml_content)

        return {
            'dict': data,
            'yaml': yaml.dump(yaml_content),
            'plain': yaml_content
        }


    def generate(self, skills: dict) -> dict:
        print(colored(f"Generating {self.topic} series outline...", "yellow"))

        save_file_name = f"{self.course_material_path}/series-{self.topic_formatted}"
        messages = self.build_series_prompt(skills['yaml'])

        completion = self.ai_client.send_prompt(messages)
        json_content = self.handle_outline_draft_response(completion)
        
        write_json_file(save_file_name, json_content)
        return json_content



  