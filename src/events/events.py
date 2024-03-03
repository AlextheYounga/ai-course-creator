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


class GenerateSkillsPromptSentToLLM(Event):
    def __init__(self, data):
        self.data = data


class GenerateSkillsResponseProcessed(Event):
    def __init__(self, data):
        self.data = data


class InvalidGenerateSkillsResponseFromLLM(Event):
    def __init__(self, data):
        self.data = data


class FailedToParseYamlFromGenerateSkillsResponse(Event):
    def __init__(self, data):
        self.data = data


class AllGenerateOutlineChunksPromptsCreated(Event):
    def __init__(self, data):
        self.data = data


class AllGenerateOutlineChunksPromptsSentToLLM(Event):
    def __init__(self, data):
        self.data = data


class InvalidOutlineChunkResponsesFromLLM(Event):
    def __init__(self, data):
        self.data = data


class FailedToParseYamlFromOutlineChunkResponses(Event):
    def __init__(self, data):
        self.data = data


class AllOutlineChunkResponsesProcessed(Event):
    def __init__(self, data):
        self.data = data


class MasterOutlineCompiledFromOutlineChunks(Event):
    def __init__(self, data):
        self.data = data


class OutlineEntitiesCreatedFromOutline(Event):
    def __init__(self, data):
        self.data = data
