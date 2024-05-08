from db.db import DB, Topic

db = DB()


class PingController:
    @staticmethod
    def ping_pong():
        topics_count = len(db.query(Topic).all())
        return {
            'message': 'pong!',
            'topics_count': topics_count
        }
