import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

course = "Ruby on Rails"
model = "gpt-3.5-turbo-1106"
save_file_name = course.lower().replace(" ", "_")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

initial_prompt = open("src/data/prompts/start.md", "r").read()
system_context = open("src/data/prompts/system.md", "r").read()

messages = [
    {"role": "system", "content": system_context},
    {"role": "user", "content": initial_prompt}
]

for i in range(15):
    payload_file = f"src/data/chat/payloads/{save_file_name}-{i}.json"
    reply_file = f"src/data/chat/replies/{save_file_name}-{i}.md"
    context_file = f"src/data/chat/context/{save_file_name}.json"

    if (i > 0):
        continue_prompt = open("src/data/prompts/continue.md", "r").read()
        messages.append({"role": "user", "content": continue_prompt})

    try:
        # Send to ChatGPT
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
        )

        messages.append(completion.choices[0].message)

        with open(context_file, 'w') as f:
            f.write(json.dumps(messages))
            f.close()

        with open(payload_file, 'w') as f:
            f.write(completion.model_dump_json())
            f.close()

        with open(reply_file, 'w') as f:
            f.write(completion.choices[0].message.content)
            f.close()

        print(f"Success: {save_file_name} reply received.")
    except Exception as e:
        print(f"Error: {e}")


# ---------- Snippets ----------
# if not os.path.exists(os.path.dirname(payload_file)):
#     os.mkdir(os.path.dirname(payload_file))
# if not os.path.exists(os.path.dirname(reply_file)):
#     os.mkdir(os.path.dirname(reply_file))
