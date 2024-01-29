from typing import Optional
import os


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
