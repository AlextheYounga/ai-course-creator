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


class GenerateSkillsResponseReceivedFromLLM(Event):
    def __init__(self, data):
        self.data = data


class GenerateSkillsResponseProcessedSuccessfully(Event):
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


class OutlineChunkResponseReceivedFromLLM(Event):
    def __init__(self, data):
        self.data = data


class OutlineChunkResponseProcessedSuccessfully(Event):
    def __init__(self, data):
        self.data = data


class InvalidOutlineChunkResponseFromLLM(Event):
    def __init__(self, data):
        self.data = data


class FailedToParseYamlFromOutlineChunkResponse(Event):
    def __init__(self, data):
        self.data = data


class AllOutlineChunkResponsesProcessedSuccessfully(Event):
    def __init__(self, data):
        self.data = data


class MasterOutlineCompiledFromOutlineChunks(Event):
    def __init__(self, data):
        self.data = data


class OutlineEntitiesCreatedFromOutline(Event):
    def __init__(self, data):
        self.data = data


# Pages

class GenerateLessonPageRequested(Event):
    def __init__(self, data):
        self.data = data


class GeneratePracticeChallengePageRequested(Event):
    def __init__(self, data):
        self.data = data


class GenerateFinalSkillChallengePageRequested(Event):
    def __init__(self, data):
        self.data = data


class GeneratePagesFromEntityRequested(Event):
    def __init__(self, data):
        self.data = data


class LessonPageResponseReceivedFromLLM(Event):
    def __init__(self, data):
        self.data = data
