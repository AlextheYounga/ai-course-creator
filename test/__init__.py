import os
import shutil
import pathlib

# sys.setrecursionlimit(2000)

app_dir = os.path.dirname(pathlib.Path(__file__).parent)
config_path = os.path.join(app_dir, 'configs')
params_file = os.path.join(config_path, 'params.yaml')
topics_file = os.path.join(config_path, 'topics.yaml')

if ((not os.path.exists(params_file)) or (not os.path.exists(topics_file))):
    shutil.copyfile(os.path.join(config_path, 'params.example.yaml'), params_file)
    shutil.copyfile(os.path.join(config_path, 'topics.example.yaml'), topics_file)

try:
    os.remove('test/data/test.db')
    os.rmdir('test/data/logs')
    os.mkdir('test/data/logs')
except:
    pass
