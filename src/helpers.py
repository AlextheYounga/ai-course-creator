from typing import Optional
from db.db import DB, Topic, Outline
from src.utils.files import read_yaml_file
import os
import yaml


def get_prompt(topic: Topic, filename: str, args: dict = {}) -> str:
    prompt_collection = topic.properties.get("prompts", 'default')
    prompt = open(f"storage/prompts/{prompt_collection}/{filename}.md", "r").read()

    if (args != None):
        for key, value in args.items():
            replace_key = f"{{{key}}}"
            prompt = prompt.replace(replace_key, value)

    return prompt


def scan_topics_file():
    topics_file = read_yaml_file("storage/topics.yaml")

    for name, properties in topics_file['topics'].items():
        existing_topic_record = DB.query(Topic).filter(Topic.name == name).first()

        if existing_topic_record:
            existing_topic_record.properties = properties
            DB.commit()
        else:
            topic_record = Topic(
                name=name,
                slug=Topic.make_slug(name),
                properties=properties
            )
            DB.add(topic_record)
            DB.commit()


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
        skills = outline.properties.get('skills', {})
        skills_file.write(yaml.dump(skills, sort_keys=False))
        skills_file.close()

    with open(f"{output_path}/{outline.name}/outline.yaml", 'w') as outline_file:
        outline_file.write(yaml.dump(outline.master_outline, sort_keys=False))
        outline_file.close()

    with open(f"{output_path}/master-outline.yaml", 'w') as outline_file:
        outline_file.write(yaml.dump(outline.master_outline, sort_keys=False))
        outline_file.close()
