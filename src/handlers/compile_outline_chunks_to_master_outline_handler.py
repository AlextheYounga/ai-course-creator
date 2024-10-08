from termcolor import colored
import os
import yaml
from db.db import DB, Outline
from src.events.events import MasterOutlineCompiledFromOutlineChunks


class CompileOutlineChunksToMasterOutlineHandler:
    def __init__(self, data: dict):
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'
        self.data = data
        self.db = DB()
        self.outline = self.db.get(Outline, data['outlineId'])
        self.topic = self.outline.topic
        self.output_path = f"{output_directory}/{self.topic.slug}"  # master outline sits at topic level
        self.series_path = f"{output_directory}/{self.topic.slug}/{self.outline.name}"


    def handle(self) -> Outline:
        if not self.outline.get_properties('outlineChunks'):
            raise Exception("OutlineChunks not found in outline properties.")

        outline_data = self._compile_outline_data_from_chunks()

        # Hash outline
        outline_hash = Outline.hash_outline(outline_data)

        # Check for existing outline hash
        existing_outline = self.db.query(Outline).filter(Outline.hash == outline_hash).first()
        if existing_outline:
            print(colored("Identical outline found. Aborting.", "red"))
            return existing_outline

        # Update outline
        self.outline.outline_data = outline_data
        self.outline.hash = outline_hash
        self.db.commit()

        # Set as Topic Master Outline
        self.topic.master_outline_id = self.outline.id
        self.db.commit()

        self._save_master_outline_to_yaml_file()

        return MasterOutlineCompiledFromOutlineChunks(self.data)


    def _compile_outline_data_from_chunks(self) -> dict:
        outline_data = []
        outline_chunks = self.outline.properties['outlineChunks']

        for course in outline_chunks:
            course = self._add_challenges_to_chapters(course)
            outline_data.append(course)

        return outline_data


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
            yaml.dump(self.outline.outline_data, yaml_file, sort_keys=False)
