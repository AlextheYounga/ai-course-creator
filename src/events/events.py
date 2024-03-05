class Event:
    """Base class for all events."""
    pass

# Outlines


class GenerateOutlineRequested(Event):
    def __init__(self, data):
        self.data = data


class NewOutlineInstantiated(Event):
    def __init__(self, data):
        self.data = data


class NewOutlineCreated(Event):
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


class GeneratePagesFromOutlineEntityRequested(Event):
    def __init__(self, data):
        self.data = data


class NoExistingPageContentForLesson(Event):
    def __init__(self, data):
        self.data = data


class NoExistingPageContentForPracticeChallenge(Event):
    def __init__(self, data):
        self.data = data


class NoExistingPageContentForFinalChallenge(Event):
    def __init__(self, data):
        self.data = data


class NewLessonPageCreatedFromExistingPage(Event):
    def __init__(self, data):
        self.data = data


class NewPracticeChallengePageCreatedFromExistingPage(Event):
    def __init__(self, data):
        self.data = data


class NewFinalChallengePageCreatedFromExistingPage(Event):
    def __init__(self, data):
        self.data = data


class ExistingPageSoftDeletedForPageRegeneration(Event):
    def __init__(self, data):
        self.data = data


class GenerateLessonPageProcessStarted(Event):
    def __init__(self, data):
        self.data = data


class GeneratePracticeChallengePageProcessStarted(Event):
    def __init__(self, data):
        self.data = data


class GenerateFinalSkillChallengePageProcessStarted(Event):
    def __init__(self, data):
        self.data = data


class LessonPagePromptCreated(Event):
    def __init__(self, data):
        self.data = data


class PracticeChallengePagePromptCreated(Event):
    def __init__(self, data):
        self.data = data


class FinalSkillChallengePagePromptCreated(Event):
    def __init__(self, data):
        self.data = data


class SummarizePagePromptCreated(Event):
    def __init__(self, data):
        self.data = data


class LessonPageSummarizedSuccessfully(Event):
    def __init__(self, data):
        self.data = data


class InvalidPageSummaryResponseFromLLM(Event):
    def __init__(self, data):
        self.data = data


class InvalidChallengePageResponseFromLLM(Event):
    def __init__(self, data):
        self.data = data


class ChallengePageResponseProcessedSuccessfully(Event):
    def __init__(self, data):
        self.data = data


class InvalidLessonPageResponseFromLLM(Event):
    def __init__(self, data):
        self.data = data


class LessonPageResponseProcessedSuccessfully(Event):
    def __init__(self, data):
        self.data = data


class FinalChallengeGenerationFailedDueToIncompleteCourse(Event):
    def __init__(self, data):
        self.data = data


class FinalSkillChallengePageResponseReceivedFromLLM(Event):
    def __init__(self, data):
        self.data = data


class PracticeChallengePageResponseReceivedFromLLM(Event):
    def __init__(self, data):
        self.data = data


class PracticeChallengeGenerationFailedDueToIncompleteChapter(Event):
    def __init__(self, data):
        self.data = data


class LessonPageResponseReceivedFromLLM(Event):
    def __init__(self, data):
        self.data = data
