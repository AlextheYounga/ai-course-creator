# flask --app app.server.app run --port 5001
import os
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from .controllers.course_material_controller import compile_course_material
from .controllers.page_controller import render_page
from .controllers.course_creator_controller import run_all_course_creator, get_course_creator_activity


# Instantiate the app
template_directory = os.path.abspath('app/client/dist')
static_folder=os.path.abspath('app/client/dist/assets')

app = Flask(__name__, template_folder=template_directory, static_folder=static_folder)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

# Load Vue App
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# API Routes
@app.route('/api/ping', methods=['GET'])
def ping_pong():
    # sanity check route
    return jsonify('pong!')


@app.route('/api/course-material', methods=['GET'])
def fetch_course_material():
    material = compile_course_material()
    return jsonify(material)


@app.route('/api/activity', methods=['GET'])
def fetch_activity():
    logs = get_course_creator_activity()
    # Returning a response back to the AJAX call
    return jsonify(logs)


@app.route('/api/page/<topic>/<course>/<chapter>/<page>', methods=['GET'])
def page(topic, course, chapter, page):
    return render_page(topic, course, chapter, page)


@app.route('/api/generate-courses', methods=['POST'])
def begin_course_generator():
    run_all_course_creator()
    # Returning a response back to the AJAX call
    return jsonify(True)
