import os
from src.scripts.initialize import initialize_project

# sys.setrecursionlimit(2000)

initialize_project()

try:
    os.remove('test/data/test.db')
    os.rmdir('test/data/logs')
    os.mkdir('test/data/logs')
except:
    pass
