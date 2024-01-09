from flask import render_template
import os
from src.utils.chat_helpers import slugify
from src.utils.files import read_json_file
import markdown

def find_page_by_keys(topic, course, chapter, page):
    # Slugify keys just in case
    topic_slug = slugify(topic)
    course_slug = slugify(course)
    chapter_slug = slugify(chapter)
    page_slug = slugify(page)

    current_path = os.getcwd()
    outline = read_json_file(f'{current_path}/out/course_material/{topic_slug}/master-outline.json')
    page_object = outline['courses'][course_slug]['chapters'][chapter_slug]['pages'][page_slug]

    return page_object


def render_page(page):
    current_path = os.getcwd()
    content = open(page['path']).read()
    html = markdown.markdown(content, extensions=['fenced_code'])
    
    partial_file_path = f"{current_path}/app/templates/partials/page-content.html"
    with open(partial_file_path, 'w') as f:
        f.write(html)

    return render_template("page.html")


# def green_stocks():
#     current_path = os.getcwd()
#     html_file_path = f"{current_path}/app/templates/partials/green_stocks_table.html"
    
#     stocks = get_green_stocks()
#     stocks.to_html(html_file_path)

#     return render_template("green_stocks.html")