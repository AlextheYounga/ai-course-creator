from db.db import DB, Prompt, Response

db = DB()


class PromptController:
    @staticmethod
    def get(id: int):
        log_record = db.query(Prompt, Response).join(
            Prompt, Response.prompt_id == Prompt.id
        ).filter(
            Prompt.id == id
        ).first()

        logs = {
            'prompt': log_record.Prompt.to_dict(),
            'response': log_record.Response.to_dict()
        }

        return logs


    @staticmethod
    def get_all():
        log_records = db.query(Prompt, Response).join(
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

        return logs
