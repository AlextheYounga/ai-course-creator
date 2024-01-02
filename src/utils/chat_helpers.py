import markdown
import re
from bs4 import BeautifulSoup

def parse_markdown(content: str) -> BeautifulSoup:
    html = markdown.markdown(content)
    soup = BeautifulSoup(html, 'html.parser')

    return soup


def slugify(text: str):
    url_safe = re.sub(r"[^a-z0-9\s-]", "", text)
    return url_safe.lower().replace(" ", "-")
