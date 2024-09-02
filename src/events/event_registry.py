from src.handlers import *
from src.events.events import *
from db.db import DB, EventStore, JobStore



class EventRegistry:
    _registry = {}

    @classmethod
    def register(cls, event_class, handler_class):
        cls._registry[event_class] = handler_class

    @classmethod
    def get_event(cls, event_name):
        return globals().get(event_name)

    @classmethod
    def get_handler(cls, event):
        if event.__class__ in cls._registry:
            handler = cls._registry[event.__class__]
            if not handler:
                raise ValueError(f"No handler registered for {event}")
            return handler(event.data)

        return None

    @classmethod
    def trigger(cls, event):
        event.handler = cls.get_handler(event)
        cls.save_event(event)  # Save event to the database
        if not event.handler: return None

        next_events = event.handler.handle()
        if not next_events: return None

        if not isinstance(next_events, list):
            next_events = [next_events]

        return next_events

    @classmethod
    def save_event(cls, event):
        db = DB()
        handler_name = event.handler.__class__.__name__ if event.handler else None
        job = db.query(JobStore).filter(JobStore.job_id == event.data.get('jobId', None)).first()

        event_store = EventStore(
            name=event.__class__.__name__,
            job_id=job.id,
            handler=handler_name,
            data=event.data
        )

        db.add(event_store)
        db.commit()

        return event_store


# Register all event handlers
# All job pipeline event handler definitions

# Starting Events
EventRegistry.register(GenerateOutlineJobRequested, InstantiateOutlineHandler)
EventRegistry.register(GeneratePagesFromOutlineJobRequested, CollectAllPagesToGenerateHandler)
EventRegistry.register(GeneratePageInteractivesJobRequested, CollectAllPagesForInteractiveGenerationHandler)
EventRegistry.register(CompileInteractivesToPagesJobRequested, CollectAllPagesForInteractiveCompilationHandler)

# Outline Event Handlers
EventRegistry.register(NewOutlineInstantiated, CreateGenerateSkillsPromptHandler)
EventRegistry.register(GenerateSkillsPromptCreated, SendGenerateSkillsPromptToOpenAIHandler)
EventRegistry.register(InvalidGenerateSkillsResponseFromOpenAI, SendGenerateSkillsPromptToOpenAIHandler)  # retry even)t
EventRegistry.register(FailedToParseYamlFromGenerateSkillsResponse, SendGenerateSkillsPromptToOpenAIHandler)
EventRegistry.register(GenerateSkillsResponseReceivedFromOpenAI, ProcessGenerateSkillsResponseHandler)
EventRegistry.register(GenerateSkillsResponseProcessedSuccessfully, CreateAllOutlineChunkPromptsHandler)
EventRegistry.register(AllGenerateOutlineChunksPromptsCreated, GetNextOutlineChunkPromptHandler)
EventRegistry.register(OutlineChunkGenerationProcessStarted, SendOutlineChunkPromptToOpenAIHandler)
EventRegistry.register(InvalidOutlineChunkResponseFromOpenAI, SendOutlineChunkPromptToOpenAIHandler)  # retry even)t
EventRegistry.register(FailedToParseYamlFromOutlineChunkResponse, SendOutlineChunkPromptToOpenAIHandler)
EventRegistry.register(OutlineChunkResponseReceivedFromOpenAI, ProcessOutlineChunkResponseHandler)
EventRegistry.register(OutlineChunkResponseProcessedSuccessfully, GetNextOutlineChunkPromptHandler)  # loop even)t
EventRegistry.register(AllOutlineChunkResponsesProcessedSuccessfully, CompileOutlineChunksToMasterOutlineHandler)
EventRegistry.register(MasterOutlineCompiledFromOutlineChunks, CreateOutlineEntitiesFromOutlineHandler)

# Page Generation Event Handlers
EventRegistry.register(CollectedAllPagesToGenerate, GetNextPageToGenerateHandler)
EventRegistry.register(GenerateLessonPageProcessStarted, CreateLessonPagePromptHandler)
EventRegistry.register(LessonPagePromptCreated, SendGenerateLessonPagePromptToOpenAIHandler)
EventRegistry.register(InvalidLessonPageResponseFromOpenAI, SendGenerateLessonPagePromptToOpenAIHandler)  # retry event
EventRegistry.register(LessonPageResponseReceivedFromOpenAI, ProcessLessonPageResponseHandler)
EventRegistry.register(LessonPageResponseProcessedSuccessfully, GenerateLessonPageSummaryHandler)
EventRegistry.register(LessonPageProcessedAndSummarizedSuccessfully, GetNextPageToGenerateHandler)  # loop event

# Page Interactives Generation Event Handlers
EventRegistry.register(CollectedAllPagesForInteractiveGeneration, GetNextPageForInteractivesGenerationHandler)
EventRegistry.register(GeneratePageInterativesProcessStarted, CalculateInteractiveCountsForPageHandler)
EventRegistry.register(InteractiveCountsCalculatedForPage, GetNextInteractivesToGenerateHandler)
EventRegistry.register(GenerateMultipleChoicePageInteractivesProcessStarted, CreateMultipleChoiceInteractivesPromptHandler)
EventRegistry.register(GenerateCodeEditorPageInteractivesProcessStarted, CreateCodeEditorInteractivesPromptHandler)
EventRegistry.register(GenerateCodepenPageInteractivesProcessStarted, CreateCodepenInteractivesPromptHandler)
EventRegistry.register(MultipleChoiceInteractivesPromptCreated, SendMultipleChoiceInteractivesPromptToOpenAIHandler)
EventRegistry.register(CodeEditorInteractivesPromptCreated, SendCodeEditorInteractivesPromptToOpenAIHandler)
EventRegistry.register(CodepenInteractivesPromptCreated, SendCodepenInteractivesPromptToOpenAIHandler)
EventRegistry.register(MultipleChoiceInteractivesResponseReceivedFromOpenAI, ProcessMultipleChoiceInteractivesResponseHandler)
EventRegistry.register(CodeEditorInteractivesResponseReceivedFromOpenAI, ProcessCodeEditorInteractivesResponseHandler)
EventRegistry.register(CodepenInteractivesResponseReceivedFromOpenAI, ProcessCodepenInteractivesResponseHandler)
EventRegistry.register(MultipleChoiceInteractiveShortcodeParsingFailed, SendMultipleChoiceInteractivesPromptToOpenAIHandler)  # retry event
EventRegistry.register(CodeEditorInteractiveShortcodeParsingFailed, SendCodeEditorInteractivesPromptToOpenAIHandler)  # retry event
EventRegistry.register(CodepenInteractiveShortcodeParsingFailed, SendCodepenInteractivesPromptToOpenAIHandler)  # retry event
EventRegistry.register(MultipleChoiceInteractivesSavedFromResponse, GetNextInteractivesToGenerateHandler)  # loop event
EventRegistry.register(CodeEditorInteractiveSavedFromResponse, GetNextInteractivesToGenerateHandler)  # loop event
EventRegistry.register(CodepenInteractiveSavedFromResponse, GetNextInteractivesToGenerateHandler)  # loop event
EventRegistry.register(PageInteractivesGenerationComplete, GetNextPageForInteractivesGenerationHandler)  # loop event

# Compile Interactives
EventRegistry.register(CollectedAllPagesForInteractiveCompilation, CompileInteractivesToLessonPagesHandler)
EventRegistry.register(CompiledInteractivesToLessonPages, CompileInteractivesToChallengePagesHandler)
EventRegistry.register(CompiledInteractivesToChallengePage, CompileInteractivesToFinalChallengePagesHandler)
