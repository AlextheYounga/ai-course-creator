from db.db import DB, Topic
from flask import jsonify


class PingController:
    @staticmethod
    def ping_pong():
        topics_count = len(DB.query(Topic).all())
        return jsonify('pong! ' + str(topics_count) + ' topics in db')
