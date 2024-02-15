import os
from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI
from src.creator.helpers import get_prompt
from db.db import DB, Outline
import yaml


load_dotenv()


class MasterOutlineCompiler:
    def __init__(self, outline_id: int):
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'

        self.outline = DB.get(Outline, outline_id)
        self.topic = self.outline.topic
        self.output_path = f"{output_directory}/{self.topic.slug}"  # master outline sits at topic level
        self.series_path = f"{output_directory}/{self.topic.slug}/{self.outline.name}"


    def compile_master_outline_from_chunks(self) -> dict:
        master_outline = []
        outline_chunks = self.outline.outline_chunks

        for course in outline_chunks:
            course = self._add_challenges_to_chapters(course)
            master_outline.append(course)

        return master_outline


    def compile(self) -> dict:
        print(colored(f"Compiling {self.topic.name} master outline...", "yellow"))
        master_outline = self.compile_master_outline_from_chunks()

        # Save to database
        self.outline.master_outline = master_outline
        outline_hash = Outline.hash_outline(master_outline)

        # Check for existing outline based on hash
        existing_outline = DB.query(Outline).filter(Outline.hash == outline_hash).first()
        if existing_outline:
            print(colored("Identical outline found. Using existing outline.", "yellow"))
            self.outline = existing_outline
        else:
            self.outline.hash = outline_hash
            DB.commit()

        # Set as Topic Master Outline
        self.topic.master_outline_id = self.outline.id
        DB.commit()

        # Save to YAML file
        os.makedirs(self.output_path, exist_ok=True)
        with open(f"{self.output_path}/master-outline.yaml", 'w') as yaml_file:
            yaml.dump(master_outline, yaml_file, sort_keys=False)

        print(colored("Done.", "green"))

        return self.outline


    # Private Methods


    def _add_challenges_to_chapters(self, course: dict) -> list:
        # Add Practice Skill Challenges
        for index, _ in enumerate(course['chapters']):
            course['chapters'][index]['pages'].append('Practice Skill Challenge')

        return {'course': course}
