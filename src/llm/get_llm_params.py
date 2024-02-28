from src.utils.files import read_yaml_file


def get_llm_params(event_name: str):
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
