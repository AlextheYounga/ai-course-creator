from src.utils.chat_helpers import parse_markdown

outline = open("tests/fixtures/responses/series.json", "r").read()
soup = parse_markdown(outline)
outline = soup.find("div", {"id": "outline"})   

outline_struct = []
for item in outline.find_all("li"):
    if item.findChildren("li") == []: continue

    header = item.find("p").get_text()

    children_ul = item.find("ul")
    children = [l.get_text() for l in children_ul.find_all("li")]

    outline_item = {"header": header, "children": children }
    outline_struct.append(outline_item)

print(len(outline_struct))

