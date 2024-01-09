import os
from src.utils.files import read_json_file

def get_slugs_from_path(path):
    dirs = path.split('/')
    page_slug = dirs.pop()
    chapter_slug = dirs.pop()
    course_slug = dirs.pop()

    if ('page-' in page_slug):
        page_slug = page_slug.split('page-')[1].replace('.md', '')
    if ('challenge-' in page_slug):
        page_slug = page_slug.split('challenge-')[1].replace('.md', '')

    return course_slug, chapter_slug, page_slug
    

def scan_material_for_existing(outline: dict) -> dict:
    # Update the outline with the existing files
    for _, data in outline['courses'].items():
        for path in data['paths']:  
            exists = os.path.exists(path)
            course_slug, chapter_slug, page_slug = get_slugs_from_path(path)
            outline['courses'][course_slug]['chapters'][chapter_slug]['pages'][page_slug]['exists'] = exists

    return outline


def compile_all_outlines():
    # Compiling all course material content in a single object
    data = []
    for dir in os.listdir('out/course_material'):
        outline = read_json_file(f'out/course_material/{dir}/master-outline.json')
        scanned_outline = scan_material_for_existing(outline)
        data.append(scanned_outline)

    return data


