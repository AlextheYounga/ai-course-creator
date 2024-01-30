from db.db import DB, Outline, Topic, Course, Chapter, Page
from flask import jsonify
from src.creator.outlines.outline_processor import OutlineProcessor


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
                outline_records = OutlineProcessor.get_outline_record_ids(last_outline.id)

                course_records = DB.query(Course).filter(
                    Course.id.in_(outline_records['courses'])
                ).all()

                for course in course_records:
                    course_object = {
                        **course.to_dict(),
                        'children': []
                    }

                    chapter_records = DB.query(Chapter).filter(
                        Chapter.id.in_(outline_records['chapters']),
                        Chapter.course_slug == course.slug
                    ).all()

                    for chapter in chapter_records:
                        page_records = DB.query(Page).filter(
                            Page.id.in_(outline_records['pages']),
                            Page.course_slug == course.slug,
                            Page.chapter_slug == chapter.slug
                        ).all()

                        chapter_object = {
                            **chapter.to_dict(),
                            'children': [page.to_dict() for page in page_records]
                        }

                        course_object['children'].append(chapter_object)
                    tree['children'].append(course_object)
            course_material.append(tree)

        return jsonify(course_material)
