# flask --app app.server.app run --port 5001
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from .controllers import *

# Instantiate the app
template_directory = os.path.abspath('app/client/public')
static_folder = os.path.abspath('app/client/public/assets')

app = Flask(__name__, template_folder=template_directory, static_folder=static_folder)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


@app.route('/', methods=['GET'])
def index():
    # Load Vue App
    return render_template('index.html')

# Topics


@app.route('/api/topics', methods=['GET'])
def get_all_topics():
    return TopicController.get_all()


@app.route('/api/topics/outlines/master/material', methods=['GET'])
def get_all_master_outline_material():
    return OutlineController.get_all_topics_master_outline_material()


# Tasks
@app.route('/api/generate', methods=['POST'])
def creator_generate():
    data = request.json
    TaskController.generate_entities(data)
    return 'Success', 200


# Outlines
@app.route('/api/outlines', methods=['GET'])
def get_all_outlines():
    return OutlineController.get_all()


@app.route('/api/outlines', methods=['POST'])
def create_outline():
    data = request.json
    return OutlineController.create(data)


@app.route('/api/outlines/<id>', methods=['GET'])
def get_outline(id: int):
    return OutlineController.get(id)


@app.route('/api/outlines/<id>/set-master', methods=['PUT'])
def set_master_outline(id: int):
    OutlineController.set_master(id)
    return 'Success', 200


# Logs
@app.route('/api/prompts/<id>', methods=['GET'])
def get_log(id: int):
    return LogController.get(id)


@app.route('/api/prompts', methods=['GET'])
def get_all_logs():
    return LogController.get_all()

# Courses


@app.route('/api/courses/<id>/content', methods=['GET'])
def get_course_content(id: int):
    return CourseController.get_course_content(id)


# Pages
@app.route('/api/pages/<id>', methods=['GET'])
def get_page(id: int):
    return PageController.get_page_html(id)


# Test
@app.route('/api/ping', methods=['GET'])
def ping_pong():
    # sanity check route
    return PingController.ping_pong()
