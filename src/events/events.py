class Event:
    """Base class for all events."""
    pass

# Outlines


class GenerateOutlineRequested(Event):
    def __init__(self, data):
        self.data = data


class NewThreadCreated(Event):
    def __init__(self, data):
        self.data = data


class NewOutlineInstantiated(Event):
    def __init__(self, data):
        self.data = data


class NewOutlineInstantiated(Event):
    def __init__(self, data):
        self.data = data


class GenerateSkillsPromptCreated(Event):
    def __init__(self, data):
        self.data = data
