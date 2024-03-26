from db.db import Topic


def get_prompt(topic: Topic, filename: str, args: dict = {}) -> str:
    prompt_collection = topic.get_properties().get("prompts", 'default')
    prompt = open(f"storage/prompts/{prompt_collection}/{filename}.md", "r").read()

    if (args != None):
        for key, value in args.items():
            replace_key = f"{{{key}}}"
            prompt = prompt.replace(replace_key, value)

    return prompt
