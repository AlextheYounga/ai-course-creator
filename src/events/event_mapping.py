# All job pipeline event handler definitions
EVENT_HANDLER_MAPPING = {
    # Starting Events
    "GenerateOutlineRequested": "InstantiateOutlineHandler",
    "GenerateOutlineMaterialRequested": "GetNextPageToGenerateFromJobHandler",
    "GeneratePagesFromOutlineEntityRequested": "GetNextPageToGenerateFromJobHandler",

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
    "GeneratePracticeChallengePageProcessStarted": "CreatePracticeSkillChallengePromptHandler",
    "GenerateFinalSkillChallengePageProcessStarted": "CreateFinalSkillChallengePromptHandler",
    "LessonPagePromptCreated": "SendGenerateLessonPagePromptToOpenAIHandler",
    "InvalidLessonPageResponseFromOpenAI": "SendGenerateLessonPagePromptToOpenAIHandler",  # retry event
    "PracticeChallengePagePromptCreated": "SendGeneratePracticeChallengePromptToOpenAIHandler",
    "InvalidPracticeChallengePageResponseFromOpenAI": "SendGeneratePracticeChallengePromptToOpenAIHandler",  # retry event
    "FinalSkillChallengePagePromptCreated": "SendGenerateFinalChallengePromptToOpenAIHandler",
    "InvalidFinalChallengePageResponseFromOpenAI": "SendGenerateFinalChallengePromptToOpenAIHandler",  # retry event
    "LessonPageResponseReceivedFromOpenAI": "ProcessLessonPageResponseHandler",
    "LessonPageResponseProcessedSuccessfully": "GenerateLessonPageSummaryHandler",
    "PracticeChallengePageResponseReceivedFromOpenAI": "ProcessPracticeChallengePageResponseHandler",
    "FinalSkillChallengePageResponseReceivedFromOpenAI": "ProcessFinalSkillChallengePageResponseHandler",
    "LessonPageProcessedAndSummarizedSuccessfully": "GetNextPageToGenerateFromJobHandler",
    "PracticeChallengePageResponseProcessedSuccessfully": "GetNextPageToGenerateFromJobHandler",
    "FinalChallengePageResponseProcessedSuccessfully": "GetNextPageToGenerateFromJobHandler",
}
