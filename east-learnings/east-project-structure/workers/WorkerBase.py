import json

from ep.ep.models.data_exchange.task_packet import TaskPacket

class WorkerBase:

    def __init__(self, context, task: TaskPacket):
        self.task = task
        self.context = context
        #self.task = TaskPacket().load_from_dict(json.loads(task_payload))

