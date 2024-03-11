from ..events.events import *
from ..handlers.pages import *
from ..handlers.complete_thread_handler import CompleteThreadHandler


class GeneratePagesEventPipeline():
    @staticmethod
    def subscribe_all(event_manager):
        event_manager.subscribe(
            events=[
                GenerateLessonPageProcessStarted,
                GeneratePracticeChallengePageProcessStarted,
                GenerateFinalSkillChallengePageProcessStarted
            ],
            handler=CheckForExistingPageMaterialHandler
        )


        event_manager.subscribe(
            events=[
                NoExistingPageContentForLesson,
                NewLessonPageCreatedFromExistingPage
            ],
            handler=CreateLessonPagePromptHandler
        )

        event_manager.subscribe(
            events=[
                NoExistingPageContentForPracticeChallenge,
                NewPracticeChallengePageCreatedFromExistingPage
            ],
            handler=CreatePracticeSkillChallengePromptHandler
        )

        event_manager.subscribe(
            events=[
                NoExistingPageContentForFinalChallenge,
                NewFinalChallengePageCreatedFromExistingPage
            ],
            handler=CreateFinalSkillChallengePromptHandler
        )

        event_manager.subscribe(
            events=[LessonPagePromptCreated],
            handler=SendGenerateLessonPagePromptToLLMHandler
        )

        event_manager.subscribe(
            events=[PracticeChallengePagePromptCreated],
            handler=SendGeneratePracticeChallengePromptToLLMHandler
        )

        event_manager.subscribe(
            events=[FinalSkillChallengePagePromptCreated],
            handler=SendGenerateFinalChallengePromptToLLMHandler
        )

        event_manager.subscribe(
            events=[LessonPageResponseReceivedFromLLM],
            handler=ProcessLessonPageResponseHandler
        )

        event_manager.subscribe(
            events=[LessonPageResponseProcessedSuccessfully],
            handler=GenerateLessonPageSummaryHandler
        )

        event_manager.subscribe(
            events=[PracticeChallengePageResponseReceivedFromLLM],
            handler=ProcessChallengePageResponseHandler
        )

        event_manager.subscribe(
            events=[FinalSkillChallengePageResponseReceivedFromLLM],
            handler=ProcessChallengePageResponseHandler
        )

        event_manager.subscribe(
            events=[GenerateMaterialFromOutlineEntityCompletedSuccessfully],
            handler=CompleteThreadHandler
        )

        return event_manager
