from db.db import DB, Prompt, Response
from flask import jsonify


class LogController:
    @staticmethod
    def get(id: int):
        log_record = DB.query(Prompt, Response).join(
            Prompt, Response.prompt_id == Prompt.id
        ).filter(
            Prompt.id == id
        ).first()

        logs = {
            'prompt': log_record.Prompt.to_dict(),
            'response': log_record.Response.to_dict()
        }

        return jsonify(logs)


    @staticmethod
    def get_all():
        log_records = DB.query(Prompt, Response).join(
            Prompt, Response.prompt_id == Prompt.id
        ).order_by(
            Response.created_at.desc()
        ).all()

        logs = []
        for log in log_records:
            logs.append({
                'prompt': log.Prompt.to_dict(),
                'response': log.Response.to_dict()
            })

        return jsonify(logs)
