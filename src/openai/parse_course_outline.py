from src.utils.parse import parse_markdown

"""
Returns list of dictionaries structure of course outline.
Example:
[
    {
        'header': Introduction to Ruby on Rails,
        'children': [
            'What is Ruby on Rails?',
            'History and evolution of Ruby on Rails',
            'Why use Ruby on Rails?'
        ]
    }
]
"""
def parse_course_outline(content) -> list:
    soup = parse_markdown(content)
    ol = soup.find("ol")

    outline_struct = []
    for item in ol.find_all("li"):
        if item.findChildren("li") == []: continue

        header = item.find("p").get_text()

        children_ul = item.find("ul")
        children = [l.get_text() for l in children_ul.find_all("li")]

        outline_item = {"header": header, "children": children }
        outline_struct.append(outline_item)
    
    return outline_struct