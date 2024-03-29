from db.db import Topic
import os


def get_prompt(topic: Topic, filename: str, args: dict = {}) -> str:
    prompt_collection = topic.get_properties().get("prompts", 'core')

    prompt_path = f"storage/prompts/{prompt_collection}/{filename}.md"

    if not os.path.exists(prompt_path):
        prompt_path = f"storage/prompts/core/{filename}.md"

    prompt = open(prompt_path, "r").read()

    if (args != None):
        for key, value in args.items():
            replace_key = f"{{{key}}}"
            prompt = prompt.replace(replace_key, value)

    return prompt
