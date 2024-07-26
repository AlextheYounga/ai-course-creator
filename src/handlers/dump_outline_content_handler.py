import os
import yaml
from db.db import DB, Outline



class DumpOutlineContentHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.outline = self.db.get(Outline, data['outlineId'])
        self.topic = self.outline.topic


    def handle(self):
        page_entities = Outline.get_entities_by_type(self.db, self.outline.id, 'Page')

        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'
        output_path = f"{output_directory}/{self.topic.slug}"

        for page in page_entities:
            if not page.content: continue
            # Write to file
            page.dump_page()


        os.makedirs(f"{output_path}/{self.outline.name}", exist_ok=True)

        with open(f"{output_path}/{self.outline.name}/skills.yaml", 'w') as skills_file:
            outline_properties = self.outline.properties or {}
            skills = outline_properties.get('skills', {})
            skills_file.write(yaml.dump(skills, sort_keys=False))
            skills_file.close()

        with open(f"{output_path}/{self.outline.name}/outline.yaml", 'w') as outline_file:
            outline_file.write(yaml.dump(self.outline.outline_data, sort_keys=False))
            outline_file.close()

        with open(f"{output_path}/master-outline.yaml", 'w') as outline_file:
            outline_file.write(yaml.dump(self.outline.outline_data, sort_keys=False))
            outline_file.close()
