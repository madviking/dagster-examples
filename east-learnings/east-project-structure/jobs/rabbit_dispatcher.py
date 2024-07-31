import json
import os
from typing import Dict

from dagster import job, op, graph, In, String
import importlib
from ep.ep.models.data_exchange.task_packet import TaskPacket
from ep.ep.utils.string_utils import camel_case
from dagster import sensor

"""
This is the raw str body of a rabbit payload, BUT it has been
verified to be of type TaskPacket by the sensor already, even
though its type here is not indicated and/or enforced.
"""
@op(
    ins={
        "task_payload": In(String)
    }
)
def process_task(context, task_payload: String):

    # TaskPacket is our custom object for passing data between services using RabbitMQ
    # Tasks dispatched are async and captured by sensor when finished

    task = TaskPacket().load_from_dict(json.loads(task_payload))
    context.log.info(f"Processing task: {task.target_routing}")
    # see if we have a file under worker.workers with the name of the task, then load it, create class and call run(payload)
    files = os.listdir(f'/opt/dagster/app/src/app/workers/{task.get_worker_category()}')

    try:
        if task.target_routing == 'production.detective.service.get_company':
            context.log.info(f"Flipped routing, should not have happened!")
            task.set_target_routing('production.dagster.data_save.sn_database2')

        if task.get_worker() + '.py' in files:
            module = importlib.import_module(f'app.workers.{task.get_worker_category()}.{task.get_worker()}')
            class_ = getattr(module, camel_case(task.get_worker()))
            instance = class_(context, task)
            result = instance.run()
        else:
            context.log.error(f"Worker for task {task.get_worker_category()}.{task.get_worker()} not found")
            return
    except Exception as e:
        context.log.error(f"Error processing task: {e.__str__()}")
        return

    context.log.info(result)
    return result

"""
loads worker and task
"""
@op
def handle_result(context, result):
    context.log.info(f"Handling result for task: {result.__str__()}")
    # Your result handling logic here

@job
def detective_dispatcher():
    result = process_task()
    handle_result(result)
