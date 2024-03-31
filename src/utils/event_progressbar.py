from db.db import DB, Thread
from ..events.events import Event
import tqdm

START_EVENTS = [
'GeneratePracticeChallengePageProcessStarted',
'GenerateFinalSkillChallengePageProcessStarted',
'GenerateLessonPageProcessStarted'
]


INCREMENT_EVENTS = [
'LessonPageResponseProcessedSuccessfully',
'ChallengePageResponseProcessedSuccessfully',
''
]




class EventProgressbar:
    def __init__(self, thread_id: int):
        self.thread = DB.get(Thread, thread_id)
        self.bar = None

    def check_event(self, event: Event):
        if event.__class__.__name__ in START_EVENTS:
            return self.start(event)

        if self.bar:
            self.update_on_event(event)

    def start(self, event: Event):
        self.bar = tqdm.tqdm(
            total=event.data['totalSteps'],
            desc=event.__class__.__name__,
            position=0,
            leave=False
        )

        return self

    def update_on_event(self, event: Event):
        if self.thread.status == "completed":
            self.bar.close()
            return

        self.bar.set_description(event.__class__.__name__)

        if event.__class__.__name__ in INCREMENT_EVENTS:
            self.bar.update(1)

    def close(self):
        self.bar.close()    