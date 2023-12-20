import os

def init():
    payload_path = 'src/data/chat/payloads'
    replies_path = 'src/data/chat/replies'
    context_path = 'src/data/chat/context'

    if not os.path.exists(payload_path):
        print('Creating data/chat/payloads directory...')
        os.mkdir(payload_path)
    if not os.path.exists(replies_path):
        print('Creating data/chat/replies directory...')
        os.mkdir(replies_path)
    if not os.path.exists(context_path):
        print('Creating data/chat/context directory...')
        os.mkdir(context_path)

    print("Project initialized.")

if __name__ == '__main__':
    init()