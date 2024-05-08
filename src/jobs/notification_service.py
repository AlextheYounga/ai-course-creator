import json
from src.services.redis_client import get_redis_client

# Wrap up pubsub in a service.
# Jobs should be able to notify the system of their status, and the system should be able to subscribe to these notifications.


class NotificationService:
    def __init__(self, redis_host, redis_port):
        redis_client = get_redis_client()
        self.redis_conn = redis_client(host=redis_host, port=redis_port)
        self.default_queue = 'notifications'

    def notify(self, message, queue_name=None):
        if queue_name is None:
            queue_name = self.default_queue
        serialized_message = json.dumps(message)
        self.redis_conn.publish(queue_name, serialized_message)

    def subscribe(self, queue_name=None):
        if queue_name is None:
            queue_name = self.default_queue
        pubsub = self.redis_conn.pubsub()
        pubsub.subscribe(queue_name)
        return pubsub
