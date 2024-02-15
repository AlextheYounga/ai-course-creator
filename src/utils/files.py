import os
import json
import zipfile
import yaml
from pathlib import Path


def read_txt_file(filepath):
    if os.path.exists(filepath):
        file = open(filepath, "r")

        items = []
        for line in file:
            stripped_line = line.strip()
            line_list = stripped_line.split()
            items.append(str(line_list[0]))

        return list(dict.fromkeys(items))
    else:
        open(filepath, 'a').close()
        return []


def write_txt_file(filepath, lst, overwrite=False):
    if overwrite == False and os.path.exists(filepath):
        has_data = read_txt_file(filepath)
        if (has_data):
            lst = list(dict.fromkeys(has_data + lst))

    with open(filepath, 'w') as f:
        for item in lst:
            f.write("%s\n" % item)


def write_json_file(path, data):
    directory = os.path.dirname(path)
    if not (os.path.exists(directory)):
        os.makedirs(directory, exist_ok=True)

    with open(path, 'w') as json_file:
        json.dump(data, json_file)


def read_json_file(path):
    txtfile = open(path, "r")
    return json.loads(txtfile.read())


def write_markdown_file(path, content):
    directory = os.path.dirname(path)
    if not (os.path.exists(directory)):
        os.makedirs(directory, exist_ok=True)

    with open(f"{path}.md", 'w') as f:
        f.write(content)
        f.close()


def read_yaml_file(filepath):
    with open(filepath, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            return None


def write_yaml_file(path, data):
    directory = os.path.dirname(path)
    if not (os.path.exists(directory)):
        os.makedirs(directory, exist_ok=True)

    with open(path, 'w') as file:
        if isinstance(data, dict) or isinstance(data, list):
            yaml.dump(data, file)
        else:
            file.write(data)


def zip_file(file_path, output_file):
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(file_path, os.path.basename(file_path))


def zip_folder(folder_path, output_file):
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        len_dir_path = len(folder_path)
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, file_path[len_dir_path:])


def unzip_folder(zip_file, output_path):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(output_path)


def scan_directory(directory):
    all_files = []
    pathlist = Path(directory).rglob('*')  # This will recursively go through all files and folders
    for path in pathlist:
        all_files.append(str(path))
    return all_files
