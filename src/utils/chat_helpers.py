import markdown
import yaml
import re
from bs4 import BeautifulSoup
from typing import Optional

def parse_markdown(content: str) -> BeautifulSoup:
    html = markdown.markdown(content)
    soup = BeautifulSoup(html, 'html.parser')

    return soup


def parse_yaml_from_markdown(content: str):
    yaml_content = content.split("yaml")[1].split("```")[0]
    data = yaml.safe_load(yaml_content)
    return data

def slugify(text: str):
    slugified = text.lower().replace(" ", "-")
    url_safe = re.sub(r"[^a-z0-9\s-]", "", slugified)
    
    return url_safe


def get_prompt(filename, replace: Optional[list[tuple]]) -> str:
    prompt = open(f"src/data/prompts/{filename}.md", "r").read()

    if (replace != None):
        for item in replace:
            prompt = prompt.replace(item[0], item[1])

    return prompt