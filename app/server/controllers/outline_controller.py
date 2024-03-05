from db.db import DB, Outline, Topic
from src.utils.helpers import dump_outline_content
from flask import jsonify


class OutlineController:
    @staticmethod
    def get(id: int):
        return jsonify(DB.get(Outline, id).to_dict())


    @staticmethod
    def create(data: dict):
        outline_data = data['outline_data']
        outline_hash = Outline.hash_outline(outline_data)

        existing_outlines = DB.query(Outline).filter(
            Outline.hash == outline_hash
        ).count()

        if existing_outlines:
            return 'Outline already exists', 409

        topic_id = data['topic_id']
        topic = DB.get(Topic, topic_id)

        properties = {
            **outline.get('properties', {}),
            'skills': data.get('skills', {})
        }

        outline = Outline.instantiate(DB, topic_id)
        outline.properties = properties
        outline.outline_data = outline_data
        outline.hash = outline_hash
        outline.file_path = Outline.default_outline_file_path(topic)

        DB.add(outline)
        DB.commit()

        Outline.create_outline_entities(DB, outline.id)

        return 'Success', 201


    @staticmethod
    def set_master(id: int):
        outline = DB.get(Outline, id)
        topic = outline.topic
        topic.master_outline_id = outline.id

        dump_outline_content(topic, outline)

        DB.add(topic)
        DB.commit()


    @staticmethod
    def get_all():
        course_material = []
        topics = DB.query(Topic).all()

        for topic in topics:
            tree = {**topic.to_dict(), 'children': []}

            outlines = DB.query(Outline).filter(
                Outline.topic_id == topic.id
            ).order_by(
                Outline.created_at.desc()
            ).all()

            for outline in outlines:
                outline_object = {**outline.to_dict(), 'children': []}
                outline_entities = Outline.get_entities(DB, outline.id)

                # Loop through courses
                for course in outline_entities['courses']:
                    course_object = {**course.to_dict(), 'children': []}

                    chapter_records = [
                        chapter for chapter in outline_entities['chapters']
                        if chapter.course_id == course.id
                    ]

                    # Loop through chapters
                    for chapter in chapter_records:
                        page_records = [
                            page for page in outline_entities['pages']
                            if (page.course_id == course.id and page.chapter_id == chapter.id)
                        ]

                        # Add chapter pages to chapter
                        chapter_object = {
                            **chapter.to_dict(),
                            'children': [page.to_dict() for page in page_records]
                        }

                        course_object['children'].append(chapter_object)
                    outline_object['children'].append(course_object)
                tree['children'].append(outline_object)
            course_material.append(tree)
        return jsonify(course_material)


    @staticmethod
    def get_all_topics_master_outline_material():
        course_material = []
        topics = DB.query(Topic).all()

        for topic in topics:
            outline = Outline.get_master_outline(DB, topic)

            tree = {**topic.to_dict(), 'children': []}

            if outline:
                outline_entities = Outline.get_entities(DB, outline.id)

                # Loop through courses
                for course in outline_entities['courses']:
                    course_object = {**course.to_dict(), 'children': []}

                    chapter_records = [
                        chapter for chapter in outline_entities['chapters']
                        if chapter.course_id == course.id
                    ]

                    # Loop through chapters
                    for chapter in chapter_records:
                        page_records = [
                            page for page in outline_entities['pages']
                            if (page.course_id == course.id and page.chapter_id == chapter.id)
                        ]

                        # Add chapter pages to chapter
                        chapter_object = {
                            **chapter.to_dict(),
                            'children': [page.to_dict() for page in page_records]
                        }

                        course_object['children'].append(chapter_object)
                    tree['children'].append(course_object)
            course_material.append(tree)
        return jsonify(course_material)
