from src.services.redis_client import get_redis_client


# A simple pluggable named queue implementation.
# The queue should be able to enqueue and dequeue jobs into different states.
# Note that nothing external knows that this is based on Redis.
class StorageQueue:
    def __init__(self, host='127.0.0.1', port=6379):
        redis_client = get_redis_client()
        self.redis = redis_client(host=host, port=port)

    """Add an item to the queue."""
    def put(self, queue_name, data):
        self.redis.lpush(queue_name, data)

    """Remove an item from the queue. Blocks until an item is available."""
    def get(self, queue_name):
        _, message = self.redis.brpop(queue_name, timeout=0)
        return message

    """Returns the last item in the queue, or None if the queue is empty."""
    def get_nowait(self, queue_name):  # Don't call this unless you're sure you need to.
        return self.redis.rpop(queue_name)

    """Returns a list of all queues matching the pattern."""
    def list_queues(self, pattern='*'):
        return self.redis.keys(pattern)

    """Flush a given queue"""
    def flush(self, queue_name):
        self.redis.delete(queue_name)

    """Flush all queues"""
    def flush_all(self):
        self.redis.flushall()

    """Returns the length of the queue."""
    def length(self, queue_name):
        return self.redis.llen(queue_name)
