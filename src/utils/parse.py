import markdown
from bs4 import BeautifulSoup

def parse_markdown(content: str) -> BeautifulSoup:
    html = markdown.markdown(content)
    soup = BeautifulSoup(html, 'html.parser')

    return soup
