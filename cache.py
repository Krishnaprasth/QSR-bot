import os
import redis

class Cache:
    def __init__(self):
        self.client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

    def exists(self, key: str) -> bool:
        return self.client.exists(key)

    def get(self, key: str) -> str:
        return self.client.get(key).decode("utf-8")

    def set(self, key: str, value: str, ex: int = 3600):
        self.client.set(key, value, ex)
