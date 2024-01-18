import os
from src.utils.files import read_json_file
from src.openai.outlines.create_outlines import main as run_create_outlines
from src.openai.page_material_creator import main as run_create_pages
from src.openai.practice_skill_challenge_creator import main as run_create_practice_skill_challenges


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
    log_path = f"{current_path}/data/logs/chat.log"

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
    topics = read_json_file(f'{current_path}/data/topics.json')

    run_create_outlines(topics)
    run_create_pages(topics)
    run_create_practice_skill_challenges(topics)
