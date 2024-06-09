import os
import string


def to_pascal_case(file_name):
    pascal_case = string.capwords(file_name.replace("_", " ")).replace(" ", "")
    return pascal_case.replace("Openai", "OpenAI")


if __name__ == "__main__":
    files = os.listdir('src/handlers')
    files.sort()

    for file in files:
        if file.endswith('.py') and file != '__init__.py':
            file_name = file[:-3]
            print(f'from .{file_name} import {to_pascal_case(file_name)}')
