import os
import sys

sys.setrecursionlimit(2000)

try:
    os.rmdir('test/data/logs')
    os.mkdir('test/data/logs')
    os.remove('test/data/test.db')
except:
    pass
