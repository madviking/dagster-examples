from app.utils.rabbit import Rabbit
from dagster import job, op, In, Out, get_dagster_logger, DynamicOut, DynamicOutput, graph, Config, DynamicPartitionsDefinition
from ep.ep.models.data_exchange.task_packet import TaskPacket
logger = get_dagster_logger()


"""
Publish a TaskPacket to RabbitMQ
"""

@op(
    ins={"task": In(TaskPacket)},
    out=Out(None)
)
def publish_task_packet(task: TaskPacket):
    if task:
        rabbit = Rabbit()
        rabbit.send_task_to_detective(task)
        logger.info(f"Published to rabbit: {task.get_payload()}")
    else:
        logger.warning("No task payload to send to RabbitMQ")
