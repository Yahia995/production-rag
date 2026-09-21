from unittest.mock import MagicMock

from app.core.queue import IngestionJobMessage, RedisJobQueue


def test_enqueue_pushes_serialized_message() -> None:
    client = MagicMock()
    queue = RedisJobQueue(client=client)

    message = IngestionJobMessage(
        job_id="job-1",
        source="doc.pdf",
        collection="python",
    )

    queue.enqueue(message)

    client.rpush.assert_called_once()
    args, _ = client.rpush.call_args
    assert args[0] == "ingestion_jobs"
    assert "job-1" in args[1]


def test_dequeue_returns_deserialized_message() -> None:
    client = MagicMock()
    client.blpop.return_value = (
        b"ingestion_jobs",
        b'{"job_id": "job-1", "source": "doc.pdf", "collection": "python"}',
    )

    queue = RedisJobQueue(client=client)
    message = queue.dequeue()

    assert message == IngestionJobMessage(
        job_id="job-1",
        source="doc.pdf",
        collection="python",
    )


def test_dequeue_returns_none_on_timeout() -> None:
    client = MagicMock()
    client.blpop.return_value = None

    queue = RedisJobQueue(client=client)

    assert queue.dequeue(timeout=1) is None


def test_queue_length_delegates_to_client() -> None:
    client = MagicMock()
    client.llen.return_value = 3

    queue = RedisJobQueue(client=client)

    assert queue.queue_length() == 3
