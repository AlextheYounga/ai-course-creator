from cuid import cuid
from .base_event import BaseEvent as Event



# Job Start Events


class GenerateOutlineRequested(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class GenerateOutlineMaterialRequested(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class GeneratePagesFromOutlineEntityRequested(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


# Outlines
class NewOutlineInstantiated(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class NewOutlineCreated(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class GenerateSkillsPromptCreated(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class GenerateSkillsResponseReceivedFromOpenAI(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class GenerateSkillsResponseProcessedSuccessfully(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class InvalidGenerateSkillsResponseFromOpenAI(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class FailedToParseYamlFromGenerateSkillsResponse(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class AllGenerateOutlineChunksPromptsCreated(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class OutlineChunkGenerationProcessStarted(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data



class OutlineChunkResponseReceivedFromOpenAI(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class OutlineChunkResponseProcessedSuccessfully(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class InvalidOutlineChunkResponseFromOpenAI(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class FailedToParseYamlFromOutlineChunkResponse(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class AllOutlineChunkResponsesProcessedSuccessfully(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class MasterOutlineCompiledFromOutlineChunks(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class OutlineEntitiesCreatedFromOutline(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data



# Pages
class GeneratePagesFromOutlineEntityRequested(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class GenerateLessonPageProcessStarted(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class GeneratePracticeChallengePageProcessStarted(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class GenerateFinalSkillChallengePageProcessStarted(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class LessonPagePromptCreated(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class PracticeChallengePagePromptCreated(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class FinalSkillChallengePagePromptCreated(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class SummarizePagePromptCreated(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class LessonPageProcessedAndSummarizedSuccessfully(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class InvalidPageSummaryResponseFromOpenAI(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class InvalidPracticeChallengePageResponseFromOpenAI(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class InvalidFinalChallengePageResponseFromOpenAI(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class PracticeChallengePageResponseProcessedSuccessfully(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class FinalChallengePageResponseProcessedSuccessfully(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class InvalidLessonPageResponseFromOpenAI(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class LessonPageResponseProcessedSuccessfully(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class FinalChallengeGenerationFailedDueToIncompleteCourse(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class FinalSkillChallengePageResponseReceivedFromOpenAI(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class PracticeChallengePageResponseReceivedFromOpenAI(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class PracticeChallengeGenerationFailedDueToIncompleteChapter(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class LessonPageResponseReceivedFromOpenAI(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data



# Finish Events
class GenerateOutlineJobFinished(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class GenerateOutlineMaterialJobFinished(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class GenerateMaterialFromOutlineEntityJobFinished(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data
