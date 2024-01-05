# flask --app app.app run
from flask import Flask, jsonify, render_template
from src.utils.compile_course_material import compile_course_material
from src.utils.files import read_txt_file

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/ajax-fetch-content', methods=['POST'])
def fetch_content():
    # Compiling all course material content in a single object
    data = compile_course_material()

    # Returning a response back to the AJAX call
    return jsonify(data)


@app.route('/ajax-fetch-activity', methods=['POST'])
def fetch_activity():
    # Reading log file
    data = open('src/data/chat/logs/chat.log').read().splitlines()
    data.reverse()

    # Returning a response back to the AJAX call
    return jsonify(data)
