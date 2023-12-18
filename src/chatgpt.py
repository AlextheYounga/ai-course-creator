import os
import json
from dotenv import load_dotenv
import openai
import time

load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")
initial_prompt 
messages = [{"role": "user", "content": prompt}]

try:
    chat_completion = openai.ChatCompletion.create(model=self.model, messages=messages)
    self.output(save_file_name, chat_completion)
    print(f"Success: {save_file_name} reply received.")
except Exception as e:
    print(f"Error: {e}")


# def output(self, save_file_name, response):
#     payload_file = f"src/data/chat/payloads/{save_file_name}.json"
#     reply_file = f"src/data/chat/replies/{save_file_name}.md"

#     # Make directories
#     if not os.path.exists(os.path.dirname(payload_file)):
#         os.mkdir(os.path.dirname(payload_file))
#     if not os.path.exists(os.path.dirname(reply_file)):
#         os.mkdir(os.path.dirname(reply_file))

#     with open(payload_file, 'w') as f:
#         f.write(json.dumps(response))
#         f.close()

#     with open(reply_file, 'w') as f:
#         f.write(response.choices[0].message.content)
#         f.close()
