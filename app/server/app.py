# flask --app app.server.app run --port 5001
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from .controllers.outline_controller import OutlineController
from .controllers.log_controller import LogController
from .controllers.ping_controller import PingController
from .controllers.page_controller import PageController



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


# API GET Routes
@app.route('/api/course-material', methods=['GET'])
def get_course_material():
    return OutlineController.get_all_course_material()


@app.route('/api/outlines', methods=['GET'])
def get_outlines():
    return OutlineController.get_all()


@app.route('/api/prompts/<id>', methods=['GET'])
def get_log(id: int):
    return LogController.get(id)


@app.route('/api/prompts', methods=['GET'])
def get_logs():
    return LogController.get_all()


@app.route('/api/page/<id>', methods=['GET'])
def get_page(id: int):
    return PageController.get_page_html(id)


@app.route('/api/ping', methods=['GET'])
def ping_pong():
    # sanity check route
    return PingController.ping_pong()

# API POST Routes


@app.route('/api/generate', methods=['POST'])
def creator_generate():
    data = request.form
