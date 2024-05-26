from db.models import Interactive
from sqlalchemy import event


@event.listens_for(Interactive, 'before_insert')
def translate_difficulty(mapper, connect, target):
    difficulty = {
        'easy': 1,
        'intermediate': 2,
        'advanced': 3,
    }

    target.difficulty = difficulty.get(target.difficulty, 2)
