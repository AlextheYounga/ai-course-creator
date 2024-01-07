# flask --app app.app run
from flask import Flask, jsonify, render_template
from src.mapping.map_course_material_to_server_payload import *

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/ajax-fetch-course-material', methods=['POST'])
def fetch_course_material():
    # Compiling all course material content in a single object
    data = map_course_material_to_server_payload()

    # Returning a response back to the AJAX call
    return jsonify(data)


@app.route('/ajax-fetch-activity', methods=['POST'])
def fetch_activity():
    # Reading log file
    data = open('data/logs/chat.log').read().splitlines()
    data.reverse()

    # Returning a response back to the AJAX call
    return jsonify(data)
