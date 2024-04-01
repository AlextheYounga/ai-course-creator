from db.db import DB, Thread
from ..events.events import Event
import progressbar


# This is a helper class to show a progress bar for events that have a total number of steps
# This was incredibly finicky to set up. Yes it is a bit hacky but it works.

INCREMENT_EVENTS = [
    'LessonPageProcessedAndSummarizedSuccessfully',
    'ChallengePageResponseProcessedSuccessfully',
    'FinalChallengePageResponseProcessedSuccessfully'
]

CLOSE_EVENTS = [
    'GenerateMaterialFromOutlineEntityCompletedSuccessfully'
]


class EventProgressbar:
    def __init__(self):
        self.bar = None
        self.max_value = None
        self.thread = None

    def setup(self, event: Event):
        self.max_value = event.data['totalSteps']
        self.thread = DB.get(Thread, event.data['threadId'])

        self.bar = progressbar.ProgressBar(
            label=f"bar-{self.thread.id}",
            suffix=' {variables.event_name}',
            variables={'event_name': event.__class__.__name__},
            max_value=self.max_value,
            redirect_stdout=True,
        )

    def update_on_event(self, event: Event):
        try:
            # If bar has not been instantiated, instantiate
            if self.bar is None:
                self.setup(event)
                self.bar.start()

            if self.bar:
                # Close out the bar and reset the bar if we are done
                if self.thread.status == 'completed' or event.__class__.__name__ in CLOSE_EVENTS:
                    self.bar.finish()
                    self.bar = None
                    return

                # The update method must be run in order to update the label name.
                # If the event is not in the INCREMENT_EVENTS list, the step will be None
                step = None
                if event.__class__.__name__ in INCREMENT_EVENTS:
                    step = self.bar.value + 1

                self.bar.update(step, event_name=event.__class__.__name__)

        except Exception as e:
            if self.bar:
                self.bar.finish()
            print(f'Progress Bar Error (this should not effect the main program): {e}')
            return


    def close(self):
        self.bar.finish()
