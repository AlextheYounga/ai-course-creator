import os
import shutil
from termcolor import colored
from openai import OpenAI
from .openai_handler import OpenAiHandler
from src.utils.files import read_json_file, write_markdown_file
from src.utils.chat_helpers import slugify, get_prompt


class SkillChallengeCreator:    
    def __init__(self, topic: str, client: OpenAI, output_path: str):
        topic_slug = slugify(topic)
        self.ai_client = client
        self.topic = topic
        self.topic_slug = topic_slug
        self.output_path = f"{output_path}/{topic_slug}"
        self.outline_path = f"{self.output_path}/master-outline.json"

        if os.path.exists(f"{self.output_path}/content"):
            shutil.rmtree(f"{self.output_path}/content")

    def prepare_datasets(self):
        pass