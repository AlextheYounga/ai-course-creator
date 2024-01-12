import markdown
import yaml
import re
from bs4 import BeautifulSoup

def parse_markdown(content: str) -> BeautifulSoup:
    html = markdown.markdown(content)
    soup = BeautifulSoup(html, 'html.parser')

    return soup


def parse_yaml_from_markdown(content: str):
    yaml_content = content.split("yaml")[1].split("```")[0]
    data = yaml.safe_load(yaml_content)
    return data