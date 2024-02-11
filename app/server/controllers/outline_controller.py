from db.db import DB, Outline, Topic
from flask import jsonify


class OutlineController:
    @staticmethod
    def get_all():
        outlines = DB.query(Outline).all()
        return jsonify([outline.to_dict() for outline in outlines])


    @staticmethod
    def get_all_course_material():
        course_material = []
        topics = DB.query(Topic).all()

        for topic in topics:
            outline = Outline.get_or_create_from_file(DB, topic.id)

            tree = {**topic.to_dict(), 'children': []}

            if outline:
                outline_entities = Outline.get_entities(DB, outline.id)

                # Loop through courses
                for course in outline_entities['courses']:
                    course_object = {**course.to_dict(), 'children': []}

                    chapter_records = [
                        chapter for chapter in outline_entities['chapters']
                        if chapter.course_slug == course.slug
                    ]

                    # Loop through chapters
                    for chapter in chapter_records:
                        page_records = [
                            page for page in outline_entities['pages']
                            if (page.course_slug == course.slug and page.chapter_slug == chapter.slug)
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
