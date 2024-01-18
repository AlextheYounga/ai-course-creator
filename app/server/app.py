# flask --app app.server.app run --port 5001
from flask import Flask, jsonify
from flask_cors import CORS
from .controllers.course_material_controller import compile_course_material
from .controllers.page_controller import render_page
from .controllers.course_creator_controller import run_all_course_creator, get_course_creator_activity


# Insantiate the app
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')




# @app.route("/")
# def home():
#     return render_template("app/client/dist/index.html")


# @app.route('/page/<topic>/<course>/<chapter>/<page>')
# def page(topic, course, chapter, page):
#     return render_page(topic, course, chapter, page)


# @app.route('/ajax-fetch-course-material', methods=['POST'])
# def fetch_course_material():
#     material = compile_course_material()
#     return jsonify(material)


# @app.route('/ajax-fetch-activity', methods=['POST'])
# def fetch_activity():
#     logs = get_course_creator_activity()
#     # Returning a response back to the AJAX call
#     return jsonify(logs)


# @app.route('/ajax-begin-course-generator', methods=['POST'])
# def begin_course_generator():
#     run_all_course_creator()
#     # Returning a response back to the AJAX call
#     return jsonify(True)
