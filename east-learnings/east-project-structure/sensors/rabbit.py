import os

from dagster import sensor, RunRequest, DefaultSensorStatus, get_dagster_logger
import aio_pika
import json
import asyncio
from typing import List

from ep.ep.models.data_exchange.task_packet import TaskPacket
logger = get_dagster_logger()

class DagsterDetectiveRunner:
    def __init__(self):
        self.connection: aio_pika.Connection = None
        self.channel: aio_pika.Channel = None
        self.queues = self._get_queues()

    async def connect_to_rabbitmq(self):
        if not self.connection or self.connection.is_closed:
            self.connection = await aio_pika.connect_robust(
                login=os.getenv('--REDACTED--'),
                password=os.getenv('--REDACTED--'),
                host='--REDACTED--',
                port=int(os.getenv('--REDACTED--',5671)),
            )
            self.channel = await self.connection.channel()

    async def get_message(self) -> str | None:
        await self.connect_to_rabbitmq()
        for queue_name in self.queues:
            queue = await self.channel.declare_queue(queue_name)
            message = await queue.get(fail=False)
            if message:
                async with message.process():
                    body = message.body.decode()
                    return body

        return None

    def _get_queues(self) -> List[str]:
        return ['dagster']


@sensor(job_name="detective_dispatcher", default_status=DefaultSensorStatus.RUNNING)
def detective_sensor(context):
    logger.info(f"Warming up sensor ... ")
    configs = {
        'login': os.getenv('--REDACTED--'),
        'password': os.getenv('--REDACTED--'),
        'port': os.getenv('--REDACTED--',5671),
        'host': os.getenv('--REDACTED--'),
    }

    logger.info(f"Got a task {json.dumps(configs)}")
    runner = DagsterDetectiveRunner()
    task_payload = asyncio.run(runner.get_message())

    if task_payload is None:
        logger.info("No task")
        return None

    # conversion to object here is only for debugging purposes
    # we are passing body as string to the dagster op
    task = TaskPacket().load_from_dict(json.loads(task_payload))

    # confirms that it is indeed a TaskPacket
    if task:
        logger.info(f"Got a task {task.get_payload()}")

        job_part_1 = task.get_worker_category()
        job_part_2 = task.get_worker()

        # IMPORTANT:
        # Dagster keeps track of the run keys and will NOT perform same run twice. So if you are testing,
        # make sure to include random part in the run_key, like a timestamp or a random number.

        # unixtime
        random = int(os.popen('date +%s').read().strip())
        run_key = f"{job_part_1}_{job_part_2}_{task.get_task_id()}_{random}"

        return RunRequest(
            run_key=run_key,
            job_name="detective_dispatcher",
            run_config={
                "ops": {
                    "process_task": {
                        "inputs": {
                            "task_payload": task_payload,
                        }
                    }
                }
            }
        )

    return None
