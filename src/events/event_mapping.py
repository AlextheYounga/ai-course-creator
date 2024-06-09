# All job pipeline event handler definitions
EVENT_HANDLER_MAPPING = {
    # Starting Events
    "GenerateOutlineJobRequested": "InstantiateOutlineHandler",
    "GeneratePagesFromOutlineJobRequested": "CollectAllPagesToGenerateHandler",
    "GeneratePageInteractivesJobRequested": "CollectAllPagesForInteractiveGenerationHandler",
    "CompileInteractivesToPagesJobRequested": "CompileInteractivesToLessonPagesHandler",

    # Outline Event Handlers
    "NewOutlineInstantiated": "CreateGenerateSkillsPromptHandler",
    "GenerateSkillsPromptCreated": "SendGenerateSkillsPromptToOpenAIHandler",
    "InvalidGenerateSkillsResponseFromOpenAI": "SendGenerateSkillsPromptToOpenAIHandler",  # retry event
    "FailedToParseYamlFromGenerateSkillsResponse": "SendGenerateSkillsPromptToOpenAIHandler",
    "GenerateSkillsResponseReceivedFromOpenAI": "ProcessGenerateSkillsResponseHandler",
    "GenerateSkillsResponseProcessedSuccessfully": "CreateAllOutlineChunkPromptsHandler",
    "AllGenerateOutlineChunksPromptsCreated": "GetNextOutlineChunkPromptHandler",
    "OutlineChunkGenerationProcessStarted": "SendOutlineChunkPromptToOpenAIHandler",
    "InvalidOutlineChunkResponseFromOpenAI": "SendOutlineChunkPromptToOpenAIHandler",  # retry event
    "FailedToParseYamlFromOutlineChunkResponse": "SendOutlineChunkPromptToOpenAIHandler",
    "OutlineChunkResponseReceivedFromOpenAI": "ProcessOutlineChunkResponseHandler",
    "OutlineChunkResponseProcessedSuccessfully": "GetNextOutlineChunkPromptHandler",  # loop event
    "AllOutlineChunkResponsesProcessedSuccessfully": "CompileOutlineChunksToMasterOutlineHandler",
    "MasterOutlineCompiledFromOutlineChunks": "CreateOutlineEntitiesFromOutlineHandler",

    # Page Generation Event Handlers
    "CollectedAllPagesToGenerate": "GetNextPageToGenerateHandler",
    "GenerateLessonPageProcessStarted": "CreateLessonPagePromptHandler",
    "LessonPagePromptCreated": "SendGenerateLessonPagePromptToOpenAIHandler",
    "InvalidLessonPageResponseFromOpenAI": "SendGenerateLessonPagePromptToOpenAIHandler",  # retry event
    "LessonPageResponseReceivedFromOpenAI": "ProcessLessonPageResponseHandler",
    "LessonPageResponseProcessedSuccessfully": "GenerateLessonPageSummaryHandler",
    "LessonPageProcessedAndSummarizedSuccessfully": "GetNextPageToGenerateHandler",  # loop event

    # Page Interactives Generation Event Handlers
    "CollectedAllPagesForInteractiveGeneration": "GetNextPageForInteractivesGenerationHandler",
    "GeneratePageInterativesProcessStarted": "CalculateInteractiveCountsForPageHandler",
    "InteractiveCountsCalculatedForPage": "GetNextInteractivesToGenerateHandler",
    "GenerateMultipleChoicePageInteractivesProcessStarted": "CreateMultipleChoiceInteractivesPromptHandler",
    "GenerateCodeEditorPageInteractivesProcessStarted": "CreateCodeEditorInteractivesPromptHandler",
    "GenerateCodepenPageInteractivesProcessStarted": "CreateCodepenInteractivesPromptHandler",
    "MultipleChoiceInteractivesPromptCreated": "SendMultipleChoiceInteractivesPromptToOpenAIHandler",
    "CodeEditorInteractivesPromptCreated": "SendCodeEditorInteractivesPromptToOpenAIHandler",
    "CodepenInteractivesPromptCreated": "SendCodepenInteractivesPromptToOpenAIHandler",
    "MultipleChoiceInteractivesResponseReceivedFromOpenAI": "ProcessMultipleChoiceInteractivesResponseHandler",
    "CodeEditorInteractivesResponseReceivedFromOpenAI": "ProcessCodeEditorInteractivesResponseHandler",
    "CodepenInteractivesResponseReceivedFromOpenAI": "ProcessCodepenInteractivesResponseHandler",
    "MultipleChoiceInteractiveShortcodeParsingFailed": "SendMultipleChoiceInteractivesPromptToOpenAIHandler",  # retry event
    "CodeEditorInteractiveShortcodeParsingFailed": "SendCodeEditorInteractivesPromptToOpenAIHandler",  # retry event
    "CodepenInteractiveShortcodeParsingFailed": "SendCodepenInteractivesPromptToOpenAIHandler",  # retry event
    "MultipleChoiceInteractivesSavedFromResponse": "GetNextInteractivesToGenerateHandler",  # loop event
    "CodeEditorInteractiveSavedFromResponse": "GetNextInteractivesToGenerateHandler",  # loop event
    "CodepenInteractiveSavedFromResponse": "GetNextInteractivesToGenerateHandler",  # loop event
    "PageInteractivesGenerationComplete": "GetNextPageForInteractivesGenerationHandler",  # loop event
    "AllInteractivesGeneratedFromPages": "CompileInteractivesToLessonPagesHandler",
    "CompiledInteractivesToLessonPages": "CompileInteractivesToChallengePagesHandler",
    "CompiledInteractivesToChallengePage": "CompileInteractivesToFinalChallengePagesHandler",
}
