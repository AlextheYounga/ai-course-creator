import webbrowser
from app.server.app import * 

def run_server():
    # Open a browser window
    url = 'http://localhost:5001/'
    webbrowser.open(url)

    # Run the Flask app
    app.run(port=5001)


if __name__ == '__main__':
    run_server()
