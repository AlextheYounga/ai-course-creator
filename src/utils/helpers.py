from db.db import DB, Topic, Outline
import os
import yaml





def dump_outline_content(topic: Topic, outline: Outline):
    topic = outline.topic
    page_entities = Outline.get_entities_by_type(DB, outline.id, 'Page')

    output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'
    output_path = f"{output_directory}/{topic.slug}"

    for page in page_entities:
        if not page.content: continue
        # Write to file
        page.dump_page()


    os.makedirs(f"{output_path}/{outline.name}", exist_ok=True)

    with open(f"{output_path}/{outline.name}/skills.yaml", 'w') as skills_file:
        outline_properties = outline.properties or {}
        skills = outline_properties.get('skills', {})
        skills_file.write(yaml.dump(skills, sort_keys=False))
        skills_file.close()

    with open(f"{output_path}/{outline.name}/outline.yaml", 'w') as outline_file:
        outline_file.write(yaml.dump(outline.outline_data, sort_keys=False))
        outline_file.close()

    with open(f"{output_path}/master-outline.yaml", 'w') as outline_file:
        outline_file.write(yaml.dump(outline.outline_data, sort_keys=False))
        outline_file.close()
