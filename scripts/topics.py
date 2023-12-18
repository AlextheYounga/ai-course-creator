import time
import os
import json
from src.chatgpt import ChatGPT

chatgpt = ChatGPT(model="gpt-4")
topics = json.load(open('src/data/prompts/topics.json'))

def create_prompt(topic):
    type = topic["type"]
    tone = topic["tone"]

    if topic["prompt"]:
        return open(topic["prompt"]).read()
    
    if type:
        prompt = open(f"src/data/prompts/specific/{type}.txt").read()
    else:
        prompt = open(f"src/data/prompts/{tone}.txt").read()

    prompt = prompt.format(name=topic["name"], category=topic["category"])
    return prompt

for topic in topics:
    save_file = f"{topic['category'].lower()}/{topic['id']}"

    if not os.path.exists(f"src/data/chat/replies/{save_file}.md"):
        name = topic["name"]
        tone = topic["tone"]
        prompt = topic["prompt"] if topic.get("prompt", False) else create_prompt(topic)

        chatgpt.chat(prompt, save_file)
    
    time.sleep(3)