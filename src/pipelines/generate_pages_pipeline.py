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
            events=[LessonPagePromptCreated],
            handler=SendGenerateLessonPagePromptToLLMHandler
        )

        # Send practice challenge prompts to LLM
        event_manager.subscribe(
            events=[PracticeChallengePagePromptCreated],
            handler=SendGeneratePracticeChallengePromptToLLMHandler
        )

        # Send final challenge prompts to LLM
        event_manager.subscribe(
            events=[FinalSkillChallengePagePromptCreated],
            handler=SendGenerateFinalChallengePromptToLLMHandler
        )

        # Process lesson page response
        event_manager.subscribe(
            events=[LessonPageResponseReceivedFromLLM],
            handler=ProcessLessonPageResponseHandler
        )


        # Process lesson page summary
        event_manager.subscribe(
            events=[LessonPageResponseProcessedSuccessfully],
            handler=GenerateLessonPageSummaryHandler
        )

        # Process practice challenge page response
        event_manager.subscribe(
            events=[PracticeChallengePageResponseReceivedFromLLM],
            handler=ProcessChallengePageResponseHandler
        )

        # Process final challenge page response
        event_manager.subscribe(
            events=[FinalSkillChallengePageResponseReceivedFromLLM],
            handler=ProcessChallengePageResponseHandler
        )

        return event_manager
