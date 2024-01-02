from src.utils.chat_helpers import parse_markdown
import json
import re

series = open("tests/fixtures/series.md", "r").read()
soup = parse_markdown(series)
code_block = soup.find("code").get_text()
code = re.sub(r"^[^\[]*", "", code_block)
content = json.loads(code)
print(content)
