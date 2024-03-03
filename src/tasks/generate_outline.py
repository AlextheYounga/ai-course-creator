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
        self.thread = CreateNewThreadHandler({'eventName': self.__class__.__name__}).handle()

    def run(self):
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
            [GenerateSkillsPromptSentToLLM],
            ProcessGenerateSkillsResponseHandler
        )

        # Generate Outline Chunks Prompts
        EVENT_MANAGER.subscribe(
            [GenerateSkillsResponseProcessed],
            CreateGenerateOutlineChunksPromptHandler
        )

        # Send Generate Outline Chunks Prompts to LLM
        EVENT_MANAGER.subscribe([
            AllGenerateOutlineChunksPromptsCreated,
            InvalidOutlineChunkResponsesFromLLM,  # retry event
            FailedToParseYamlFromOutlineChunkResponses  # retry event
        ], SendGenerateOutlineChunksPromptsToLLMHandler)

        # Process Outline Chunks Responses
        EVENT_MANAGER.subscribe(
            [AllGenerateOutlineChunksPromptsSentToLLM],
            ProcessGenerateOutlineChunksResponsesHandler
        )

        # Compile Outline Chunks to Master Outline
        EVENT_MANAGER.subscribe(
            [AllOutlineChunkResponsesProcessed],
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
                'threadId': self.thread.id,
                'topicId': self.topic.id
            })
        )

        print('Done')
