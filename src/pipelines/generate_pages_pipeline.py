from ..events.events import *
from ..handlers.pages import *


class GeneratePagesEventPipeline():
    @staticmethod
    def subscribe_all(event_manager):
        # Check for existing page material
        event_manager.subscribe(
            events=[
                GenerateLessonPageProcessStarted,
                GeneratePracticeChallengePageProcessStarted,
                GenerateFinalSkillChallengePageProcessStarted
            ],
            handler=CheckForExistingPageMaterialHandler
        )

        # Create lesson page prompt
        event_manager.subscribe(
            events=[
                NoExistingPageContentForLesson,
                NewLessonPageCreatedFromExistingPage
            ],
            handler=CreateLessonPagePromptHandler
        )

        # Create practice challenge prompt
        event_manager.subscribe(
            events=[
                NoExistingPageContentForPracticeChallenge,
                NewPracticeChallengePageCreatedFromExistingPage
            ],
            handler=CreatePracticeSkillChallengePromptHandler
        )

        # Create final challenge prompt
        event_manager.subscribe(
            events=[
                NoExistingPageContentForFinalChallenge,
                NewFinalChallengePageCreatedFromExistingPage
            ],
            handler=CreateFinalSkillChallengePromptHandler
        )

        # Send lesson prompts to LLM
        event_manager.subscribe(
            events=[
                LessonPagePromptCreated,
                InvalidLessonPageResponseFromOpenAI  # retry event
            ],
            handler=SendGenerateLessonPagePromptToOpenAIHandler
        )

        # Send practice challenge prompts to LLM
        event_manager.subscribe(
            events=[
                PracticeChallengePagePromptCreated,
                InvalidPracticeChallengePageResponseFromOpenAI  # retry event
            ],
            handler=SendGeneratePracticeChallengePromptToOpenAIHandler
        )

        # Send final challenge prompts to LLM
        event_manager.subscribe(
            events=[
                FinalSkillChallengePagePromptCreated,
                InvalidFinalChallengePageResponseFromOpenAI  # retry event
            ],
            handler=SendGenerateFinalChallengePromptToOpenAIHandler
        )

        # Process lesson page response
        event_manager.subscribe(
            events=[LessonPageResponseReceivedFromOpenAI],
            handler=ProcessLessonPageResponseHandler
        )


        # Process lesson page summary
        event_manager.subscribe(
            events=[LessonPageResponseProcessedSuccessfully],
            handler=GenerateLessonPageSummaryHandler
        )

        # Process practice challenge page response
        event_manager.subscribe(
            events=[PracticeChallengePageResponseReceivedFromOpenAI],
            handler=ProcessChallengePageResponseHandler
        )

        # Process final challenge page response
        event_manager.subscribe(
            events=[FinalSkillChallengePageResponseReceivedFromOpenAI],
            handler=ProcessChallengePageResponseHandler
        )

        # Get next page
        event_manager.subscribe(
            events=[
                LessonPageProcessedAndSummarizedSuccessfully,
                ChallengePageResponseProcessedSuccessfully,
                FinalChallengePageResponseProcessedSuccessfully
            ],
            handler=GetNextPageToGenerateFromThreadHandler
        )

        return event_manager
