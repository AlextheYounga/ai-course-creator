# flask --app app.server.app run --port 5001
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from .controllers.outline_controller import OutlineController
from .controllers.log_controller import LogController
from .controllers.ping_controller import PingController
from .controllers.page_controller import PageController
from .controllers.creator_controller import CreatorController
from .controllers.topic_controller import TopicController



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


@app.route('/api/topics', methods=['GET'])
def get_all_topics():
    return TopicController.get_all()


@app.route('/api/master-outline-course-material', methods=['GET'])
def get_all_master_outline_material():
    return OutlineController.get_all_topics_master_outline_material()


@app.route('/api/generate', methods=['POST'])
def creator_generate():
    data = request.json
    CreatorController.generate_entities(data)
    return 'Success', 200


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


@app.route('/api/prompts/<id>', methods=['GET'])
def get_log(id: int):
    return LogController.get(id)


@app.route('/api/prompts', methods=['GET'])
def get_all_logs():
    return LogController.get_all()


@app.route('/api/page/<id>', methods=['GET'])
def get_page(id: int):
    return PageController.get_page_html(id)


@app.route('/api/ping', methods=['GET'])
def ping_pong():
    # sanity check route
    return PingController.ping_pong()
