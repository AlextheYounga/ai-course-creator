import yaml
import re
import os
from typing import Optional


def slugify(text: str):
    slugified = text.lower().replace(" ", "-")
    url_safe = re.sub(r"[^a-z0-9\s-]", "", slugified)

    return url_safe


def get_prompt(filename, replace: Optional[list[tuple]]) -> str:
    prompt = open(f"data/prompts/{filename}.md", "r").read()

    if (replace != None):
        for item in replace:
            prompt = prompt.replace(item[0], item[1])

    return prompt


def copy_master_outline_to_yaml(file_path: str, outline: dict):
    yaml_outline = []
    for course_data in outline['courses'].values():
        course = {
            'course': {
                'courseName': course_data['courseName'],
                'chapters': []
            }
        }

        for chapter_data in course_data['chapters'].values():
            chapter = {'name': chapter_data['name'], 'pages': []}

            for page_data in chapter_data['pages'].values():
                name = page_data['name']
                chapter['pages'].append(name)
            course['course']['chapters'].append(chapter)
        yaml_outline.append(course)


    directory = os.path.dirname(file_path)
    with open(f"{directory}/master-outline.yaml", 'w') as yaml_file:
        yaml.dump(yaml_outline, yaml_file, sort_keys=False)
