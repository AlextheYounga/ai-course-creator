import os
from src.utils.chat_helpers import slugify
from src.utils.files import read_json_file, write_json_file, scan_directory


def compile_output():
    compiled_output = []
    output_folder = "src/data/chat/course_material"
    topics_json = read_json_file('src/data/topics.json')

    for topic in topics_json:
        topic_slug = slugify(topic)
        topic_exists = os.path.exists(f"{output_folder}/{topic_slug}")

        if not topic_exists:
            compiled_output.append({
                'topic': topic,
                'slug': topic_slug,
                'exists': False,
            })
            continue


        all_paths = scan_directory(f"{output_folder}/{topic_slug}/")
        master_outline = read_json_file(f"{output_folder}/{topic}/master-outline.json")
        series_outline = read_json_file(f"{output_folder}/{topic}/series-{topic}.json")
        skills = read_json_file(f"{output_folder}/{topic}/skills-{topic}.json")
        courses_list = [item['courseName'] for item in master_outline]

        topic_object = {
            'topic': topic,
            'slug': topic_slug,
            'allPaths': all_paths,
            'courseList': courses_list,
            'outline': master_outline,
            'nestedPaths': {topic_slug: {}},
            'series': series_outline,
            'skills': skills,
            'courses': []
        }

        for outline in master_outline:
            course_name = outline['courseName']
            course_path = f"{output_folder}/{topic_slug}"
            course_exists = os.path.exists(course_path)
            course_slug = slugify(outline['courseName'])
            topic_object['nestedPaths'][topic_slug][course_slug] = {}

            chapters_list = [c['chapterName'] for c in outline['chapters']]

            course_object = {
                'topicName': topic,
                'courseName': course_name,
                'outline': outline,
                'slug': course_slug,
                'chaptersList': chapters_list,
                'path': course_path if course_exists else None,
                'exists': course_exists,
                'chapters': []
            }


            for chapter in outline['chapters']:
                chapter_name = chapter['chapterName']
                chapter_slug = slugify(chapter['chapterName'])
                chapter_path = f"{output_folder}/{topic_slug}/content/{course_slug}/{chapter_slug}"
                chapter_exists = os.path.exists(chapter_path)
                pages_list = chapter['pages']
                topic_object['nestedPaths'][topic_slug][course_slug][chapter_slug] = [slugify(page) for page in pages_list]

                chapter_object = {
                    'topicName': topic,
                    'courseName': course_name, 
                    'chapterName': chapter_name,
                    'slug': chapter_slug,
                    'exists': chapter_exists,
                    'pagesList': pages_list,
                    'pageFiles': os.listdir(chapter_path) if chapter_exists else [],
                    'path': chapter_path if chapter_exists else None,
                    'childPaths': scan_directory(chapter_path) if chapter_exists else None,
                    'pages': []
                }

                if not chapter_exists:
                    course_object['chapters'].append(chapter_object)
                    continue
                
                # Scan pages in chapter
                for page in pages_list:
                    page_slug = slugify(page)
                    page_path = f"{output_folder}/{topic_slug}/content/{course_slug}/{chapter_slug}/page-{page_slug}.md"
                    page_exists = os.path.exists(page_path)

                    page_object = {
                        'topicName': topic,
                        'courseName': course_name,
                        'chapterName': chapter,
                        'pageName': page,
                        'exists': page_exists,
                        'slug': page_slug,
                        'fileName': page if page_exists else None,
                        'data': open(page_path).read() if page_exists else None,
                        'path': page_path if page_exists else None
                    }

                    chapter_object['pages'].append(page_object)
                course_object['chapters'].append(chapter_object)
            topic_object['courses'].append(course_object)
        compiled_output.append(topic_object)

    write_json_file(f"{output_folder}/compiled-output.json", topic_object)
    return compiled_output
