from app.core.queue import IngestionJobMessage, RedisJobQueue


def test_enqueue_and_dequeue_round_trip(redis_client) -> None:
    queue = RedisJobQueue(client=redis_client)

    message = IngestionJobMessage(
        job_id="job-1",
        source="docs/asyncio.md",
        collection="python",
    )

    queue.enqueue(message)
    dequeued = queue.dequeue(timeout=1)

    assert dequeued == message


def test_queue_length_reflects_pending_jobs(redis_client) -> None:
    queue = RedisJobQueue(client=redis_client)

    queue.enqueue(IngestionJobMessage(job_id="job-1", source="a.md", collection="python"))
    queue.enqueue(IngestionJobMessage(job_id="job-2", source="b.md", collection="python"))

    assert queue.queue_length() == 2


def test_dequeue_times_out_on_empty_queue(redis_client) -> None:
    queue = RedisJobQueue(client=redis_client)

    result = queue.dequeue(timeout=1)

    assert result is None
