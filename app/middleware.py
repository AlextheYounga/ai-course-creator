from flask import render_template
from src.openai.outline_creator import run_outline_creator
from src.openai.page_material_creator import run_page_creator
import os


def _parse_output_folder():
    pass
    # output_folder = "src/data/chat/course_material"
    # courses = {}
    # for _root, dirs in os.walk(output_folder):

    #     for dir in dirs:
    #         courses[dir] = {}

    #         for _root, dirs in os.walk(f"{output_folder}/{dir}"):
    #             for dir in dirs:
    #                 if (dir == 'content'):





        # for file in files:
        #     hits = []

        #     data = json.load(open(f"{chunk_dir}/{file}"))

        #     letter = file.split("-")[0]
        #     index = file.split("-")[1].split(".")[0]

        #     for slug in data:
        #         if os.path.exists(f"scrapers/company_websites/data/website_html/{letter}/{slug}.html"):
        #             hits.append(slug)

        #     if len(hits) != 0:
        #         print(f"scrapers/company_websites/data/working/hits/{letter}-{index}.txt", len(hits))
        #         write_txt_file(f"scrapers/company_websites/data/working/hits/{letter}-{index}.txt", hits)


def generate_outlines():
    run_outline_creator()


def generate_pages():
    run_page_creator()


def index_page():
    # current_path = os.getcwd()
    # partial_file = f"{current_path}/src/app/templates/partials/progress.html"

    # output = _parse_output_folder()
    # output.to_html(partial_file)

    return render_template("index.html")
