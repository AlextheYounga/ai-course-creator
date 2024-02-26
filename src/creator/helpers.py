from typing import Optional
from db.db import DB, Topic, Outline
import os
import yaml


def get_prompt(topic: Topic, filename: str, replace: Optional[list[tuple]]) -> str:
    prompt_collection = topic.properties.get("prompt_collection", 'default')
    prompt = open(f"storage/prompts/{prompt_collection}/{filename}.md", "r").read()

    if (replace != None):
        for item in replace:
            prompt = prompt.replace(item[0], item[1])

    return prompt


def dump_outline_content(topic: Topic, outline: Outline):
    topic = outline.topic
    page_entities = Outline.get_entities_by_type(DB, outline.id, 'Page')

    output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'
    output_path = f"{output_directory}/{topic.slug}"

    for page in page_entities:
        if not page.content: continue
        # Write to file
        page.dump_page()


    os.makedirs(f"{output_path}/{outline.name}", exist_ok=True)

    with open(f"{output_path}/{outline.name}/skills.yaml", 'w') as skills_file:
        skills_file.write(yaml.dump(outline.skills, sort_keys=False))
        skills_file.close()

    with open(f"{output_path}/{outline.name}/outline.yaml", 'w') as outline_file:
        outline_file.write(yaml.dump(outline.master_outline, sort_keys=False))
        outline_file.close()

    with open(f"{output_path}/master-outline.yaml", 'w') as outline_file:
        outline_file.write(yaml.dump(outline.master_outline, sort_keys=False))
        outline_file.close()
