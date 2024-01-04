# flask --app app.app run
from flask import Flask, jsonify, render_template
from src.utils.compile_course_material import compile_course_material

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/")
def home():
    return render_template("index.html")


@app.route('/ajax-fetch-content', methods=['POST'])
def fetch_content():
    data = compile_course_material()

    # Returning a response back to the AJAX call
    return jsonify(data)
