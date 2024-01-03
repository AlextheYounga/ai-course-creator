import os
from functools import reduce
from src.utils.files import read_json_file, scan_directory


def output_controller():
    output = {}
    output_folder = "src/data/chat/course_material"

    output['paths'] = scan_directory(output_folder)
    
    for topic in os.listdir(output_folder):
        # Scan topics
        output[topic] = {}

        output[topic]['master'] = read_json_file(f"{output_folder}/{topic}/master-outline.json")
        output[topic]['series'] = read_json_file(f"{output_folder}/{topic}/series-{topic}.json")
        output[topic]['skills'] = read_json_file(f"{output_folder}/{topic}/skills-{topic}.json")

        # Scan topic folder
        for dir in os.listdir(f"{output_folder}/{topic}"):
            # Scan content folder
            if (dir == 'content'):
                output[topic]['content'] = {}

                # Scan courses in folder
                for course in os.listdir(f"{output_folder}/{topic}/{dir}"):
                    output[topic]['content'][course] = {}

                    # Scan chapters in course
                    for chapter in os.listdir(f"{output_folder}/{topic}/{dir}/{course}"):
                        output[topic]['content'][course][chapter] = []
                        pages = os.listdir(f"{output_folder}/{topic}/{dir}/{course}/{chapter}")

                        # Scan pages in chapter
                        for page in pages:
                            if (page):
                                output[topic]['content'][course][chapter].append({
                                    'path': f"{output_folder}/{topic}/{dir}/{course}/{chapter}/{page}",
                                    'data': open(f"{output_folder}/{topic}/{dir}/{course}/{chapter}/{page}").read()
                                })

                # Scan outlines folder
                if (dir == 'course-outlines'):
                    output[topic]['outlines'] = {}
                    outlines = os.listdir(f"{output_folder}/{topic}/{dir}")

                    for outline in outlines:
                        outline_data = read_json_file(f"{output_folder}/{topic}/{dir}/{outline}")
                        outline_name = outline.replace('outline-', '').replace('.json', '')
                        output[topic]['outlines'][outline_name] = outline_data

    return output


