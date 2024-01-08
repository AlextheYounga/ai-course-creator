import os
import shutil
from termcolor import colored
from openai import OpenAI
from .openai_handler import OpenAiHandler
from src.utils.files import read_json_file, write_markdown_file
from src.utils.chat_helpers import slugify, get_prompt


class PracticeSkillChallengeCreator:    
    def __init__(self, topic: str, client: OpenAI, output_path: str):
        topic_slug = slugify(topic)
        self.ai_client = client
        self.topic = topic
        self.topic_slug = topic_slug
        self.output_path = f"{output_path}/{topic_slug}"
        self.outline_path = f"{self.output_path}/master-outline.json"
        self.master_outline = self.get_topic_outline()


    def get_topic_outline(self):
        if not os.path.exists(self.outline_path):
            raise Exception("Course outline not found.")

        try:
            return read_json_file(self.outline_path)
        except Exception as e:
            print(colored(f"Error reading course outline: {e}", "red"))
            return None
        
    def prepare_datasets(self, course_slug):
        datasets = []
        for course in self.master_outline['courses']:
            if course['slug'] == course_slug:
                paths = course['paths']
                for path in paths:
                    if (os.path.exists(path)):
                        page_content = open(path).read()
                        datasets.append({"role": "system", "content": page_content})
        return datasets