from db.db import DB, Thread
from ..events.events import Event
from progressbar import ProgressBar, FormatLabel, UnknownLength

INCREMENT_EVENTS = [
    'OutlineChunkResponseReceivedFromOpenAI',
    'GeneratePracticeChallengePageProcessStarted',
    'GenerateFinalSkillChallengePageProcessStarted',
    'GenerateLessonPageProcessStarted'
]


class EventProgressbar:
    def __init__(self, thread_id: int):
        self.thread = DB.get(Thread, thread_id)
        self.bar = None


    def start(self):
        self.bar = ProgressBar(
            suffix=' {variables.event_name}',
            variables={'event_name': 'Initializing...'},
            max_value=UnknownLength,
            redirect_stdout=True,
        )

        return self


    def update_on_event(self, event: Event):
        if self.thread.status == "completed" or self.bar.value == self.bar.max_value:
            self.bar.finish()
            return

        # Check for max_value
        if self.bar.max_value == UnknownLength:
            if event.data.get('totalSteps', False):
                self.bar.max_value = event.data['totalSteps']
            else:
                return
            
        step = self.bar.value
        if event.__class__.__name__ in INCREMENT_EVENTS:
            step = step + 1

        self.bar.update(step, event_name=event.__class__.__name__)

