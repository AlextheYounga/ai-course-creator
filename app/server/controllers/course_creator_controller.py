import os
from src.utils.files import read_json_file
from src.creator.course_creator import CourseCreator


def _prune_logs(logs: list):
    pruned_logs = []
    for log in logs:
        if '127.0.0.1' in log: continue
        pruned_logs.append(log)
    return pruned_logs


def get_course_creator_activity():
    # Reading log file
    logs = []
    current_path = os.getcwd()
    log_path = f"{current_path}/storage/logs/chat.log"

    if (os.path.exists(log_path)):
        logs = open(log_path).read()

        if len(logs) > 0:
            logs = logs.splitlines()
            logs = _prune_logs(logs)
            logs.reverse()
        else:
            logs = []

    return logs


def run_all_course_creator():
    current_path = os.getcwd()
    topics = read_json_file(f'{current_path}/storage/topics.json')
    CourseCreator.run_all(topics)
