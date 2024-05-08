# uvicorn app.server.app:app --port=5001 --reload
import os
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .controllers import *
load_dotenv()

app = FastAPI()

if os.getenv('APP_ENV') == 'development':
    origins = [
        "http://localhost",
        "http://localhost:5173",  # Vue dev server
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/", status_code=status.HTTP_200_OK)
def read_root():
    return {"Hello": "World"}


# Threads
@app.get('/api/jobs', status_code=status.HTTP_200_OK)
def get_all_threads():
    return JobController.get_all()


# Topics
@app.get('/api/topics', status_code=status.HTTP_200_OK)
def get_all_topics():
    return TopicController.get_all()


@app.post('/api/topics', status_code=status.HTTP_201_CREATED)
def new(data: dict):
    return TopicController.new(data['topicName'])


@app.delete('/api/topics/{id}', status_code=status.HTTP_204_NO_CONTENT)
def destroy(id: int):
    TopicController.destroy(id)


@app.get('/api/topics/materials', status_code=status.HTTP_200_OK)
def get_all_topics_materials():
    return TopicController.get_all_topics_materials()


# Jobs
@app.post('/api/jobs/generate', status_code=status.HTTP_201_CREATED)
def request_generate(data: dict):
    return JobController.determine_job(data)


# Outlines
@app.get('/api/outlines/materials', status_code=status.HTTP_200_OK)
def get_all_outlines_materials():
    return OutlineController.get_all_outlines_materials()


@app.post('/api/outlines', status_code=status.HTTP_201_CREATED)
def create_outline(data: dict):
    return OutlineController.create(data)


@app.get('/api/outlines/{id}', status_code=status.HTTP_200_OK)
def get_outline(id: int):
    return OutlineController.get(id)


@app.put('/api/outlines/{id}/set-master', status_code=status.HTTP_201_CREATED)
def set_master_outline(id: int):
    OutlineController.set_master(id)
    return 'Success', 200


# Outline Entities
@app.put('/api/outline/{id}/entities/{entity_type}', status_code=status.HTTP_201_CREATED)
def get_outline_entities(id: int, entity_type: str):
    return OutlineEntityController.get_entities(id, entity_type)


# Prompts
@app.get('/api/prompts/{id}', status_code=status.HTTP_200_OK)
def get_log(id: int):
    return PromptController.get(id)


@app.get('/api/prompts', status_code=status.HTTP_200_OK)
def get_all_logs():
    return PromptController.get_all()


# Courses
@app.get('/api/courses/{id}/content', status_code=status.HTTP_200_OK)
def get_course_content(id: int):
    return CourseController.get_course_content(id)


# Pages
@app.get('/api/pages/{id}', status_code=status.HTTP_200_OK)
def get_page(id: int):
    return PageController.get_page(id)


# Test
@app.get('/api/ping', status_code=status.HTTP_200_OK)
def ping_pong():
    # sanity check route
    return PingController.ping_pong()
