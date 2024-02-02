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
