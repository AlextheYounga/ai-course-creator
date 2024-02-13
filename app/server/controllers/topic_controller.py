from db.db import DB, Topic
from flask import jsonify


class TopicController:
    @staticmethod
    def get_all():
        topics = []
        topic_records = DB.query(Topic).all()

        # Append outline count
        for topic in topic_records:
            outline_count = len(topic.outlines)
            topics.append({
                **topic.to_dict(),
                "outline_count": outline_count
            })

        return jsonify(topics)
