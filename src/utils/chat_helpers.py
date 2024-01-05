import markdown
import re
from bs4 import BeautifulSoup
from typing import Optional

def parse_markdown(content: str) -> BeautifulSoup:
    html = markdown.markdown(content)
    soup = BeautifulSoup(html, 'html.parser')

    return soup


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