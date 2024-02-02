from typing import Optional
from db.db import DB, Page, Outline
import os
import yaml


def get_prompt(filename, replace: Optional[list[tuple]]) -> str:
    prompt = open(f"storage/prompts/{filename}.md", "r").read()

    if (replace != None):
        for item in replace:
            prompt = prompt.replace(item[0], item[1])

    return prompt


def get_current_outline_number(topic_slug: str, output_path: str = 'out') -> int:
    series_numbers = []
    series_path = f"{output_path}/{topic_slug}"
    dir_items = os.listdir(series_path)

    for item in dir_items:
        if 'series' in item:
            series_number = int(item.split('-')[1])
            series_numbers.append(series_number)

    return max(series_number)


def dump_pages_from_outline(outline_id: int):
    outline = DB.get(Outline, outline_id)
    topic = outline.topic
    entities = Outline.get_entities()

    output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'
    output_path = f"{output_directory}/{topic.slug}"

    page_records = []

    for page in page_records:
        if not page.content: continue
        # Write to file
        Page.dump_page([page])


    with open(f"{output_path}/{outline.name}/skills.yaml", 'w') as skills_file:
        skills_file.write(yaml.dump(outline.skills, sort_keys=False))
        skills_file.close()

    with open(f"{output_path}/{outline.name}/outline.yaml", 'w') as outline_file:
        outline_file.write(yaml.dump(outline.master_outline, sort_keys=False))
        outline_file.close()
