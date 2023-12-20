import os
import json

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
    with open(path, 'w') as json_file:
        json.dump(data, json_file)


def read_json_file(path):
    txtfile = open(path, "r")
    return json.loads(txtfile.read())

