import json
import os

import pika

# this refers to our shared library which we haven't made public at this point
from ep.ep.models.data_exchange.task_packet import TaskPacket


class Rabbit:
    def __init__(self):
        self.connection = self._get_connection()
        self.channel = self.connection.channel()

    def __del__(self):
        self.close()

    def _get_connection(self):
        rabbitmq_user = os.getenv('--REDACTED--')
        rabbitmq_pass = os.getenv('--REDACTED--')
        rabbitmq_port = os.getenv('--REDACTED--')
        rabbitmq_vhost = os.getenv('--REDACTED--')
        #rabbitmq_host = os.getenv('--REDACTED--')
        rabbitmq_host = '--redacted--'

        print(rabbitmq_user, rabbitmq_pass, rabbitmq_port, rabbitmq_vhost, rabbitmq_host)

        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
        parameters = pika.ConnectionParameters(rabbitmq_host, rabbitmq_port, credentials=credentials)
        return pika.BlockingConnection(parameters)

    def publish_to_rabbit(self, task: dict, queue: str):
        payload = json.dumps(task)
        self.channel.queue_declare(queue=queue)
        self.channel.basic_publish(exchange='', routing_key=queue, body=payload)

    def send_task_to_detective(self, task: TaskPacket):
        payload = json.dumps(task.get_payload())
        self.channel.queue_declare(queue=task.get_outgoing_queue())
        self.channel.basic_publish(exchange='', routing_key=task.get_outgoing_queue(), body=payload)

    def close(self):
        if hasattr(self, 'connection') and self.connection is not None:
            self.connection.close()
