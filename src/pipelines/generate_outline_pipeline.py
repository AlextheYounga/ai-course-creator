from ..events.events import *
from ..handlers.outlines import *


class GenerateOutlineEventPipeline():
    @staticmethod
    def subscribe_all(event_manager):
        # Instantiate Outline
        event_manager.subscribe(
            events=[GenerateOutlineRequested],
            handler=InstantiateOutlineHandler
        )

        # Create Generate Skills Prompt
        event_manager.subscribe(
            events=[NewOutlineInstantiated],
            handler=CreateGenerateSkillsPromptHandler
        )

        # Send Generate Skills Prompt to LLM
        event_manager.subscribe(
            events=[
                GenerateSkillsPromptCreated,
                InvalidGenerateSkillsResponseFromLLM,  # retry event
                FailedToParseYamlFromGenerateSkillsResponse  # retry event
            ],
            handler=SendGenerateSkillsPromptToLLMHandler)

        # Process Response
        event_manager.subscribe(
            events=[GenerateSkillsResponseReceivedFromLLM],
            handler=ProcessGenerateSkillsResponseHandler
        )

        # Generate Outline Chunks Prompts
        event_manager.subscribe(
            events=[GenerateSkillsResponseProcessedSuccessfully],
            handler=CreateAllOutlineChunkPromptsHandler
        )

        # Send All Generate Outline Chunks Prompts to LLM
        event_manager.subscribe(
            events=[
                AllGenerateOutlineChunksPromptsCreated,
                InvalidOutlineChunkResponseFromLLM,  # retry event
                FailedToParseYamlFromOutlineChunkResponse  # retry event
            ],
            handler=SendAllOutlineChunkPromptsToLLMHandler
        )

        # Process Each Outline Chunk Response
        event_manager.subscribe(
            events=[OutlineChunkResponseReceivedFromLLM],
            handler=ProcessOutlineChunkResponseHandler
        )

        # Compile Outline Chunks to Master Outline
        event_manager.subscribe(
            events=[AllOutlineChunkResponsesProcessedSuccessfully],
            handler=CompileOutlineChunksToMasterOutlineHandler
        )

        # Create Outline Entities from Outline
        event_manager.subscribe(
            events=[MasterOutlineCompiledFromOutlineChunks],
            handler=CreateOutlineEntitiesFromOutlineHandler
        )

        return event_manager
