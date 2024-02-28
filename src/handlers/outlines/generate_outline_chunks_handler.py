import os
from db.db import DB, Outline
from termcolor import colored
from openai import OpenAI
from helpers import get_prompt
from src.utils.chunks import chunks_list
import yaml
import progressbar


class GenerateOutlineChunksHandler:
    def __init__(self, outline_id: int, llm: OpenAI):
        self.llm_handler = llm
        self.outline = DB.get(Outline, outline_id)
        self.topic = self.outline.topic
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'
        self.output_path = f"{output_directory}/{self.topic.slug}"  # master outline sits at topic level
        self.series_path = f"{output_directory}/{self.topic.slug}/{self.outline.name}"


    def handle(self):
        skills = self.outline.skills
        if skills == None:
            raise Exception("Skills must be generated before generating outlines.")

        skill_chunks = chunks_list(skills, 2)

        with progressbar.ProgressBar(max_value=len(skill_chunks), prefix='Generating outline chunk: ', redirect_stdout=True).start() as bar:
            for chunk in skill_chunks:
                self._generate_chunk(chunk)
                bar.increment()

        return self.outline


    def _generate_chunk(self, skills_chunk: dict) -> dict:
        print(colored(f"Generating {self.topic.name} outline chunk...", "yellow"))

        messages = self._build_outline_chunk_simple_prompt(skills_chunk)

        # Send to ChatGPT
        options = {'yamlExpected': True}
        validated_response = self.llm_handler.send_prompt('outline-chunk', messages, options)

        existing_outline_chunks = self.outline.outline_chunks or []
        outline_chunk = validated_response['dict']
        existing_outline_chunks = existing_outline_chunks + outline_chunk

        # Save to database
        self.outline.outline_chunks = existing_outline_chunks
        DB.commit()

        # Save to YAML file
        outlines_path = f"{self.series_path}/outlines"
        os.makedirs(outlines_path, exist_ok=True)
        chunk_index = len(os.listdir(outlines_path)) + 1 if os.path.exists(outlines_path) else 1
        with open(f"{outlines_path}/outline-{chunk_index}.yaml", 'w') as yaml_file:
            yaml.dump(outline_chunk, yaml_file, sort_keys=False)

        print(colored("Done.", "green"))

        return self.outline


    def _build_outline_chunk_simple_prompt(self, skills_chunk: dict) -> list[dict]:
        # Build message payload
        general_system_prompt = get_prompt(self.topic, 'system/general', {'topic': self.topic.name})
        skills_system_prompt = get_prompt(self.topic, 'system/outlines/tune-skills', {
            'topic': self.topic.name,
            'skills': yaml.dump(skills_chunk)
        })

        outline_chunks_prompt = ''
        if self.outline.outline_chunks:
            outline_chunks_prompt = get_prompt(self.topic, 'system/outlines/tune-outline-chunks', {
                'chunks': yaml.dump(self.outline.outline_chunks)
            })

        system_tuning_prompt = "\n".join([skills_system_prompt, outline_chunks_prompt])
        combined_system_prompt = "\n".join([general_system_prompt, system_tuning_prompt])
        user_prompt = get_prompt(self.topic, 'user/outlines/outline-chunk', {'topic': self.topic.name})

        return [
            {"role": "system", "content": combined_system_prompt},
            {"role": "user", "content": user_prompt}
        ]
