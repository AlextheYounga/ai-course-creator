from db.db import DB, Topic
from ..events.event_manager import EVENT_MANAGER
from ..events.events import *
from src.handlers.outlines import *
from src.handlers.create_new_thread_handler import CreateNewThreadHandler
from src.handlers.complete_thread_handler import CompleteThreadHandler

"""
EVENT_MANAGER.subscribe([Event], Handler)
EVENT_MANAGER.trigger(Event(data))

See `docs/tasks/generate-outline-flow.md` for more information
"""


class GenerateOutline:
    def __init__(self, topic_id: int):
        EVENT_MANAGER.refresh()

        self.topic = DB.get(Topic, topic_id)

    def run(self):
        thread = CreateNewThreadHandler({'eventName': self.__class__.__name__}).handle()

        # Instantiate Outline
        EVENT_MANAGER.subscribe(
            events=[GenerateOutlineRequested],
            handler=InstantiateOutlineHandler
        )

        # Create Generate Skills Prompt
        EVENT_MANAGER.subscribe(
            events=[NewOutlineInstantiated],
            handler=CreateGenerateSkillsPromptHandler
        )

        # Send Generate Skills Prompt to LLM
        EVENT_MANAGER.subscribe(
            events=[
                GenerateSkillsPromptCreated,
                InvalidGenerateSkillsResponseFromLLM,  # retry event
                FailedToParseYamlFromGenerateSkillsResponse  # retry event
            ],
            handler=SendGenerateSkillsPromptToLLMHandler)

        # Process Response
        EVENT_MANAGER.subscribe(
            events=[GenerateSkillsResponseReceivedFromLLM],
            handler=ProcessGenerateSkillsResponseHandler
        )

        # Generate Outline Chunks Prompts
        EVENT_MANAGER.subscribe(
            events=[GenerateSkillsResponseProcessedSuccessfully],
            handler=CreateAllOutlineChunkPromptsHandler
        )

        # Send All Generate Outline Chunks Prompts to LLM
        EVENT_MANAGER.subscribe(
            events=[
                AllGenerateOutlineChunksPromptsCreated,
                InvalidOutlineChunkResponseFromLLM,  # retry event
                FailedToParseYamlFromOutlineChunkResponse  # retry event
            ],
            handler=SendAllOutlineChunkPromptsToLLMHandler
        )

        # Process Each Outline Chunk Response
        EVENT_MANAGER.subscribe(
            events=[OutlineChunkResponseReceivedFromLLM],
            handler=ProcessOutlineChunkResponseHandler
        )

        # Compile Outline Chunks to Master Outline
        EVENT_MANAGER.subscribe(
            events=[AllOutlineChunkResponsesProcessedSuccessfully],
            handler=CompileOutlineChunksToMasterOutlineHandler
        )

        # Create Outline Entities from Outline
        EVENT_MANAGER.subscribe(
            events=[MasterOutlineCompiledFromOutlineChunks],
            handler=CreateOutlineEntitiesFromOutlineHandler
        )

        EVENT_MANAGER.subscribe(
            events=[OutlineGenerationProcessCompletedSuccessfully],
            handler=CompleteThreadHandler
        )

        # Trigger starting event
        EVENT_MANAGER.trigger(
            GenerateOutlineRequested({
                'threadId': thread.id,
                'topicId': self.topic.id
            })
        )

        print('Done')
