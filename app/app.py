# flask --app app.app run
from flask import Flask, jsonify, render_template
from .controllers.base_controller import compile_all_outlines
from .controllers.page_controller import find_page_by_keys, render_page


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/")
def home():
    return render_template("index.html")

@app.route('/page/<topic>/<course>/<chapter>/<page>')
def page(topic, course, chapter, page):
    page = find_page_by_keys(topic, course, chapter, page)
    return render_page(page)


@app.route('/ajax-fetch-course-material', methods=['POST'])
def fetch_course_material():
    data = compile_all_outlines()
    return jsonify(data)


@app.route('/ajax-fetch-activity', methods=['POST'])
def fetch_activity():
    # Reading log file
    data = open('data/logs/chat.log').read().splitlines()
    data.reverse()

    # Returning a response back to the AJAX call
    return jsonify(data)
