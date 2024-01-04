import os
from flask import render_template
from src.openai.outline_creator import run_outline_creator
from src.openai.page_material_creator import run_page_creator
from src.utils.compile_output import compile_output


def generate_outlines():
    run_outline_creator()


def generate_pages():
    run_page_creator()


def ajax_fetch_output():
    output = compile_output()
    return output


def index_page():
    # current_path = os.getcwd()
    # partial_file = f"{current_path}/src/app/templates/partials/progress.html"

    # output = _parse_output_folder()
    # output.to_html(partial_file)
    output = compile_output()
    return render_template("index.html")
