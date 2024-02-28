from db.db import Topic
from src.utils.files import read_yaml_file


def get_prompt(topic: Topic, filename: str, args: dict = {}) -> str:
    prompt_collection = topic.properties.get("prompts", 'default')
    prompt = open(f"storage/prompts/{prompt_collection}/{filename}.md", "r").read()

    if (args != None):
        for key, value in args.items():
            replace_key = f"{{{key}}}"
            prompt = prompt.replace(replace_key, value)

    return prompt


def process_prompt_params(event_name: str):
    params_file = read_yaml_file('params.yaml')
    prompt_params = params_file['prompts'].get(event_name, {})
    global_params = params_file['global']

    params = {
        **global_params,
        **prompt_params,
    }

    for key in list(params.keys()):
        if params[key] is None:
            del params[key]

    return params
