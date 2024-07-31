from app.utils.rabbit import Rabbit
from dagster import job, op, In, execute_job, Out

@op(ins={'message': In(dict)}, out=Out())
def send_to_rabbitmq(message: dict):
    rabbit = Rabbit()
    rabbit.publish_to_rabbit(message, 'detective_web')

