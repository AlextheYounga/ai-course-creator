# All job pipeline event handler definitions
EVENT_HANDLER_MAPPING = {
    # Starting Events
    "GenerateOutlineJobRequested": "InstantiateOutlineHandler",
    "GeneratePagesFromOutlineJobRequested": "GetNextPageToGenerateFromJobHandler",
    "GeneratePageInteractivesJobRequested": "CalculateInteractiveCountsForPageHandler",

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
    "OutlineChunkResponseProcessedSuccessfully": "GetNextOutlineChunkPromptHandler",
    "AllOutlineChunkResponsesProcessedSuccessfully": "CompileOutlineChunksToMasterOutlineHandler",
    "MasterOutlineCompiledFromOutlineChunks": "CreateOutlineEntitiesFromOutlineHandler",

    # Page Generation Event Handlers
    "GenerateLessonPageProcessStarted": "CreateLessonPagePromptHandler",
    "LessonPagePromptCreated": "SendGenerateLessonPagePromptToOpenAIHandler",
    "InvalidLessonPageResponseFromOpenAI": "SendGenerateLessonPagePromptToOpenAIHandler",  # retry event
    "LessonPageResponseReceivedFromOpenAI": "ProcessLessonPageResponseHandler",
    "LessonPageResponseProcessedSuccessfully": "GenerateLessonPageSummaryHandler",
    "LessonPageProcessedAndSummarizedSuccessfully": "GetNextPageToGenerateFromJobHandler",

    # Page Interactives Generation Event Handlers
    "InteractiveCountsCalculatedForPage": "GetNextPageInteractivesToGenerateHandler",
    "GenerateMultipleChoicePageInteractivesProcessStarted": "CreateMultipleChoiceInteractiveBatchPromptHandler",
    "GenerateCodeEditorPageInteractiveProcessStarted": "CreateCodeEditorInteractivePromptHandler",
    "GenerateCodepenPageInteractiveProcessStarted": "CreateCodepenInteractivePromptHandler",
    "MultipleChoiceInteractiveBatchPromptCreated": "SendMultipleChoiceInteractiveBatchPromptToOpenAIHandler",
    "CodeEditorInteractivePromptCreated": "SendCodeEditorInteractivePromptToOpenAIHandler",
    "CodepenInteractivePromptCreated": "SendCodepenInteractivePromptToOpenAIHandler",
    "MultipleChoiceInteractiveBatchResponseReceivedFromOpenAI": "ProcessMultipleChoiceInteractiveBatchResponseHandler",
    "CodeEditorInteractiveResponseReceivedFromOpenAI": "ProcessCodeEditorInteractiveResponseHandler",
    "CodepenInteractiveResponseReceivedFromOpenAI": "ProcessCodepenInteractiveResponseHandler",
    "MultipleChoiceInteractiveShortcodeParsingFailed": "SendMultipleChoiceInteractiveBatchPromptToOpenAIHandler",  # retry event
    "CodeEditorInteractiveShortcodeParsingFailed": "SendCodeEditorInteractivePromptToOpenAIHandler",  # retry event
    "CodepenInteractiveShortcodeParsingFailed": "SendCodepenInteractivePromptToOpenAIHandler",  # retry event
    "MultipleChoiceInteractivesSavedFromResponse": "GetNextPageInteractivesToGenerateHandler",
    "CodeEditorInteractiveSavedFromResponse": "GetNextPageInteractivesToGenerateHandler",
    "CodepenInteractiveSavedFromResponse": "GetNextPageInteractivesToGenerateHandler",
    "PageInteractivesGenerationComplete": "DetermineInteractiveCompilationForPagesHandler",
    "LessonPageReadyForInteractiveCompilation": "CompileInteractivesToLessonPageHandler",
    "ChallengePageReadyForInteractiveCompilation": "CompileInteractivesToChallengePageHandler",
    "FinalChallengePageReadyForInteractiveCompilation": "CompileInteractivesToFinalChallengePageHandler",
}
