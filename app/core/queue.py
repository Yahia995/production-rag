import json
from dataclasses import asdict, dataclass
from typing import cast

import redis

from app.core.config import get_settings

_INGESTION_QUEUE_KEY = "ingestion_jobs"


@dataclass(frozen=True, slots=True)
class IngestionJobMessage:
    job_id: str
    source: str
    collection: str


class RedisJobQueue:
    """Thin wrapper around Redis list operations for job coordination."""

    def __init__(self, client: redis.Redis | None = None) -> None:
        settings = get_settings()

        self.client: redis.Redis = client or cast(
            redis.Redis, redis.from_url(settings.redis_url)
        )

    def enqueue(self, message: IngestionJobMessage) -> None:
        self.client.rpush(_INGESTION_QUEUE_KEY, json.dumps(asdict(message)))

    def dequeue(self, timeout: int = 0) -> IngestionJobMessage | None:
        result = self.client.blpop([_INGESTION_QUEUE_KEY], timeout=timeout)

        if result is None:
            return None

        _, payload = cast(tuple[bytes, bytes], result)

        return IngestionJobMessage(**json.loads(payload))

    def queue_length(self) -> int:
        return cast(int, self.client.llen(_INGESTION_QUEUE_KEY))
