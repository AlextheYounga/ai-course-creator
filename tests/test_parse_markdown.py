from src.utils.parse import parse_markdown
import json
import re

# First test
# outline = open("tests/fixtures/outline.md", "r").read()
# soup = parse_markdown(outline)
# ol = soup.find("ol")

# outline_struct = []
# for item in ol.find_all("li"):
#     if item.findChildren("li") == []: continue

#     header = item.find("p").get_text()

#     children_ul = item.find("ul")
#     children = [l.get_text() for l in children_ul.find_all("li")]

#     outline_item = {"header": header, "children": children }
#     outline_struct.append(outline_item)

# print(len(outline_struct))

# Second test
series = open("tests/fixtures/series.md", "r").read()
soup = parse_markdown(series)
code_block = soup.find("code").get_text()
code = re.sub(r"^[^\[]*", "", code_block)
content = json.loads(code)
print(content)
