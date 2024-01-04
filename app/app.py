# flask --app app.app run
from flask import Flask, jsonify
from app.middleware import index_page, ajax_fetch_output

app = Flask(__name__)

@app.route("/")
def home():
    return index_page()

@app.route('/ajax-fetch-output', methods=['POST'])
def fetch_output():
    data = ajax_fetch_output()

    # Returning a response back to the AJAX call
    return jsonify(data)
