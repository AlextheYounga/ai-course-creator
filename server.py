import uvicorn
import webbrowser
import subprocess
import threading


def run_client():
    subprocess.run("vite", cwd="./app/client")


def run_api():
    uvicorn.run("app.server.app:app", host="localhost", port=5001)


def run_server():
    # Open a browser window
    url = 'http://localhost:5173/'
    webbrowser.open(url)

    api = threading.Thread(target=run_api)
    client = threading.Thread(target=run_client)

    api.start()
    client.start()



if __name__ == '__main__':
    run_server()
