from db.db import DB, Topic
from ..events.event_manager import EVENT_MANAGER
from ..events.events import *
from src.handlers.outlines import *
from src.handlers.create_new_thread_handler import CreateNewThreadHandler

"""
EVENT_MANAGER.subscribe([Event], Handler)
EVENT_MANAGER.trigger(Event(data))
"""


class GenerateOutline:
    def __init__(self, topic_id: int):
        self.topic = DB.get(Topic, topic_id)

    def run(self):
        thread = CreateNewThreadHandler({'eventName': self.__class__.__name__}).handle()

        # Instantiate Outline
        EVENT_MANAGER.subscribe(
            [GenerateOutlineRequested],
            InstantiateOutlineHandler
        )

        # Create Generate Skills Prompt
        EVENT_MANAGER.subscribe(
            [NewOutlineInstantiated],
            CreateGenerateSkillsPromptHandler
        )

        # Send Generate Skills Prompt to LLM
        EVENT_MANAGER.subscribe([
            GenerateSkillsPromptCreated,
            InvalidGenerateSkillsResponseFromLLM,  # retry event
            FailedToParseYamlFromGenerateSkillsResponse  # retry event
        ], SendGenerateSkillsPromptToLLMHandler)

        # Process Response
        EVENT_MANAGER.subscribe(
            [GenerateSkillsResponseReceivedFromLLM],
            ProcessGenerateSkillsResponseHandler
        )

        # Generate Outline Chunks Prompts
        EVENT_MANAGER.subscribe(
            [GenerateSkillsResponseProcessedSuccessfully],
            CreateAllOutlineChunkPromptsHandler
        )

        # Send All Generate Outline Chunks Prompts to LLM
        EVENT_MANAGER.subscribe([
            AllGenerateOutlineChunksPromptsCreated,
            InvalidOutlineChunkResponseFromLLM,  # retry event
            FailedToParseYamlFromOutlineChunkResponse  # retry event
        ], SendAllOutlineChunkPromptsToLLMHandler)

        # Process Each Outline Chunk Response
        EVENT_MANAGER.subscribe(
            [OutlineChunkResponseReceivedFromLLM],
            ProcessOutlineChunkResponseHandler
        )

        # Compile Outline Chunks to Master Outline
        EVENT_MANAGER.subscribe(
            [AllOutlineChunkResponsesProcessedSuccessfully],
            CompileOutlineChunksToMasterOutlineHandler
        )

        # Create Outline Entities from Outline
        EVENT_MANAGER.subscribe(
            [MasterOutlineCompiledFromOutlineChunks],
            CreateOutlineEntitiesFromOutlineHandler
        )

        # Trigger starting event
        EVENT_MANAGER.trigger(
            GenerateOutlineRequested({
                'threadId': thread.id,
                'topicId': self.topic.id
            })
        )

        print('Done')
