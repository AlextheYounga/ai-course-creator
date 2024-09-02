import uvicorn
import webbrowser
import subprocess
import threading


def run_client():
    subprocess.run("./build.sh", cwd="app/client", shell=True)


def run_api():
    uvicorn.run("app.server.app:app", host="localhost", port=5001)


def run_server():
    # Open a browser window
    api = threading.Thread(target=run_api)
    client = threading.Thread(target=run_client)

    api.start()
    client.start()

    url = 'http://localhost:5173/'
    webbrowser.open(url)



if __name__ == '__main__':
    run_server()
