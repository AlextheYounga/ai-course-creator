import os


def get_redis_client():
    env = os.getenv('APP_ENV', 'testing')
    if env == 'testing':
        import fakeredis
        return fakeredis.FakeRedis

    import redis
    return redis.Redis
