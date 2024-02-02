from db.db import DB, Outline, Topic
from flask import jsonify


class OutlineController:
    @staticmethod
    def get_all_course_material():
        course_material = []
        topics = DB.query(Topic).all()

        for topic in topics:
            last_outline = DB.query(Outline).filter(
                Outline.topic_id == topic.id
            ).order_by(
                Outline.id.desc()
            ).first()

            tree = {
                **topic.to_dict(),
                'children': []
            }

            if last_outline:
                outline_entities = Outline.get_entities(DB, last_outline.id)

                for course in outline_entities['courses']:
                    course_object = {
                        **course.to_dict(),
                        'children': []
                    }

                    chapter_records = [
                        chapter for chapter in outline_entities['chapters']
                        if chapter.course_slug == course.slug
                    ]

                    for chapter in chapter_records:
                        page_records = [
                            page for page in outline_entities['pages']
                            if (page.course_slug == course.slug and page.chapter_slug == chapter.slug)
                        ]

                        chapter_object = {
                            **chapter.to_dict(),
                            'children': [page.to_dict() for page in page_records]
                        }

                        course_object['children'].append(chapter_object)
                    tree['children'].append(course_object)
            course_material.append(tree)

        return jsonify(course_material)
