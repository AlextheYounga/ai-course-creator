import os
from src.utils.files import read_json_file



def _get_slugs_from_path(path):
    dirs = path.split('/')
    page_slug = dirs.pop()
    chapter_slug = dirs.pop()
    course_slug = dirs.pop()

    if ('page-' in page_slug):
        page_slug = page_slug.split('page-')[1].replace('.md', '')
    if ('challenge-' in page_slug):
        page_slug = page_slug.split('challenge-')[1].replace('.md', '')

    return course_slug, chapter_slug, page_slug


def _scan_material_for_existing(outline: dict) -> dict:
    # Update the outline with the existing files
    for data in outline['courses'].values():
        for path in data['paths']:
            exists = os.path.exists(path)
            course_slug, chapter_slug, page_slug = _get_slugs_from_path(path)
            outline['courses'][course_slug]['chapters'][chapter_slug]['pages'][page_slug]['exists'] = exists

    return outline



def compile_course_material():
    # Compiling all course material content in a single object
    current_path = os.getcwd()
    material_path = f"{current_path}/out/course_material"
    data = []

    if (not os.path.exists(material_path)): 
        return data

    if (len(os.listdir(material_path)) > 0): 
        for dir in os.listdir(material_path):
            outline_path = f"{material_path}/{dir}/master-outline.json"

            if (not os.path.exists(outline_path)): 
                continue

            outline = read_json_file(outline_path)
            scanned_outline = _scan_material_for_existing(outline)

            if (scanned_outline):
                data.append(scanned_outline)

    return data
