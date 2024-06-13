from cuid import cuid
from .base_event import BaseEvent as Event



# Job Start Events
class GenerateOutlineJobRequested(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class GeneratePagesFromOutlineJobRequested(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class GeneratePageInteractivesJobRequested(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class CompileInteractivesToPagesJobRequested(Event):
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
class CollectedAllPagesToGenerate(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class GenerateLessonPageProcessStarted(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class LessonPagePromptCreated(Event):
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


class LessonPageResponseReceivedFromOpenAI(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


# Interactives
class CollectedAllPagesForInteractiveGeneration(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class GeneratePageInterativesProcessStarted(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class InteractiveCountsCalculatedForPage(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class GenerateMultipleChoicePageInteractivesProcessStarted(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class GenerateCodeEditorPageInteractivesProcessStarted(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class GenerateCodepenPageInteractivesProcessStarted(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class MultipleChoiceInteractivesPromptCreated(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class CodeEditorInteractivesPromptCreated(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class CodepenInteractivesPromptCreated(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class MultipleChoiceInteractivesResponseReceivedFromOpenAI(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class CodeEditorInteractivesResponseReceivedFromOpenAI(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class CodepenInteractivesResponseReceivedFromOpenAI(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class MultipleChoiceInteractiveShortcodeParsingFailed(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class CodeEditorInteractiveShortcodeParsingFailed(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class CodepenInteractiveShortcodeParsingFailed(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class MultipleChoiceInteractivesSavedFromResponse(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class CodeEditorInteractiveSavedFromResponse(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class CodepenInteractiveSavedFromResponse(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class CollectedAllPagesForInteractiveCompilation(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class CompiledInteractivesToLessonPages(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class CompiledInteractivesToChallengePage(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class CompiledInteractivesToFinalChallengePage(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class PageInteractivesGenerationComplete(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data


class AllInteractivesGeneratedFromPages(Event):
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


class GenerateOutlinePagesJobFinished(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data
