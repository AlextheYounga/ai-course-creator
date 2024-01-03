# flask --app app.app run
from flask import Flask
from app.middleware import index_page

app = Flask(__name__)


@app.route("/")
def home():
    return index_page()

# @app.post("/generate-outlines")
# def generate_outlines():
#     return "<p>Hello, World!</p>"

# @app.route("/")
# def home():
#     return index_page()