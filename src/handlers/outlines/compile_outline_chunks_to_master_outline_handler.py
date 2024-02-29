from db.db import DB, Outline
from ...utils.log_handler import LOG_HANDLER
import os
import yaml
from termcolor import colored


class CompileOutlineChunksToMasterOutlineHandler:
    def __init__(self, outline_id: int):
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'

        self.outline = DB.get(Outline, outline_id)
        self.topic = self.outline.topic
        self.output_path = f"{output_directory}/{self.topic.slug}"  # master outline sits at topic level
        self.series_path = f"{output_directory}/{self.topic.slug}/{self.outline.name}"


    def handle(self):
        if not self.outline.properties.get('outlineChunks', False):
            raise Exception("OutlineChunks not found in outline properties.")

        master_outline = self._compile_master_outline_from_chunks()

        # Hash outline
        outline_hash = Outline.hash_outline(master_outline)

        # Check for existing outline hash
        existing_outline = DB.query(Outline).filter(Outline.hash == hash).first()
        if existing_outline:
            print(colored("Identical outline found. Aborting.", "red"))
            return existing_outline

        # Update outline
        self.outline.master_outline = master_outline
        self.outline.hash = outline_hash

        # Set as Topic Master Outline
        self.topic.master_outline_id = self.outline.id
        DB.commit()

        self._save_master_outline_to_yaml_file()

        return self.outline


    def _compile_master_outline_from_chunks(self) -> dict:
        master_outline = []
        outline_chunks = self.outline.properties['outlineChunks']

        for course in outline_chunks:
            course = self._add_challenges_to_chapters(course)
            master_outline.append(course)

        return master_outline


    def _add_challenges_to_chapters(self, course: dict) -> list:
        # Add Practice Skill Challenges
        for index, _ in enumerate(course['chapters']):
            course['chapters'][index]['pages'].append('Practice Skill Challenge')

        # Add Final Skill Challenge
        fsc_chapter = {
            "name": "Final Skill Challenge",
            "pages": ["Final Skill Challenge"]
        }
        course['chapters'].append(fsc_chapter)

        return {'course': course}


    def _save_master_outline_to_yaml_file(self):
        # Save to YAML file
        os.makedirs(self.output_path, exist_ok=True)
        with open(f"{self.output_path}/master-outline.yaml", 'w') as yaml_file:
            yaml.dump(self.outline.master_outline, yaml_file, sort_keys=False)
