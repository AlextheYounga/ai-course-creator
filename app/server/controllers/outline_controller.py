from db.db import DB, Outline, Topic
from src.handlers.create_new_outline_handler import CreateNewOutlineHandler
from src.handlers.dump_outline_content_handler import DumpOutlineContentHandler

db = DB()


class OutlineController:
    @staticmethod
    def get(id: int):
        return db.get(Outline, id).to_dict()


    @staticmethod
    def create(data: dict):
        outline_created = CreateNewOutlineHandler(data).handle()
        return outline_created.data['outlineId']


    @staticmethod
    def set_master(id: int):
        outline = db.get(Outline, id)
        topic = outline.topic
        topic.master_outline_id = outline.id

        DumpOutlineContentHandler({
            'outlineId': outline.id,
            'topicId': topic.id
        }).handle()

        db.add(topic)
        db.commit()


    @staticmethod
    def get_all_outlines_materials():
        """
        Returns: topics->outlines->courses->chapters->pages
        """
        course_material = []

        topics = db.query(Topic).all()
        if not topics: return []

        for topic in topics:
            topic_data = {**topic.to_dict(), 'outlines': []}

            outlines = db.query(Outline).filter(
                Outline.topic_id == topic.id
            ).order_by(
                Outline.created_at.desc()
            ).all()

            for outline in outlines:
                outline_object = {**outline.to_dict(), 'courses': []}
                outline_entities = Outline.get_entities(db, outline.id)

                # Loop through courses
                for course in outline_entities['courses']:
                    course_object = {**course.to_dict(), 'chapters': []}

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
                            'pages': [page.to_dict() for page in page_records]
                        }

                        course_object['chapters'].append(chapter_object)
                    outline_object['courses'].append(course_object)
                topic_data['outlines'].append(outline_object)
            course_material.append(topic_data)
        return course_material
