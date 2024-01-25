
import string
import random
import re
from datetime import datetime
from hashlib import md5


def slugify(text: str):
    slugified = text.lower().replace(" ", "-")
    url_safe = re.sub(r"[^a-z0-9\s-]", "", slugified)

    return url_safe


def id_generator(size=6):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))

def timestamp_id():
    return datetime.now().strftime('%Y%m%d%H%M%S')


def string_hash(string):
    # Deterministic hash from string
    text = string.strip().encode()
    return md5(text).hexdigest()