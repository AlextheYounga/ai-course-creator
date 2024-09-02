class BaseEvent:
    def __init__(self):
        self.data = None
        self.id = None
        self.handler = None


    def serialize(self):
        return {
            'eventId': self.id,
            'eventName': self.__class__.__name__,
            'eventData': self.data,
        }
