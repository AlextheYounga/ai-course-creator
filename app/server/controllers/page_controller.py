from flask import render_template
import os
from src.utils.strings import slugify
from src.utils.files import read_json_file
import markdown

def _find_page_by_keys(topic, course, chapter, page):
    # Slugify keys just in case
    topic_slug = slugify(topic)
    course_slug = slugify(course)
    chapter_slug = slugify(chapter)
    page_slug = slugify(page)

    current_path = os.getcwd()
    outline = read_json_file(f'{current_path}/out/course_material/{topic_slug}/master-outline.json')
    page_object = outline['courses'][course_slug]['chapters'][chapter_slug]['pages'][page_slug]

    return page_object


def render_page(topic, course, chapter, page):
    page = _find_page_by_keys(topic, course, chapter, page)

    current_path = os.getcwd()
    content = open(page['path']).read()
    html = markdown.markdown(content, extensions=['fenced_code'])
    
    partial_file_path = f"{current_path}/app/templates/partials/page-content.html"
    with open(partial_file_path, 'w') as f:
        f.write(html)

    return render_template("page.html")