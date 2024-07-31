import json

from app.workers.WorkerBase import WorkerBase
from ep.ep.apis.database1.database1 import Database1
from ep.ep.models.data_exchange.task_packet import TaskPacket


"""
Processing task: {'target_routing': 'production.dagster.data_save.number_search', 'return_routing': '', 'error_routing': 'production.dagster.errors.detective_errors', 'routing_history': ['production.detective.web.number_search', 'production.dagster.data_save.number_search', 'production.detective.web.number_search'], 'task_id': 358446000048441015, 'id': 358446000048441015, 'error': [], 'data': {'priority': 'high', 'linkedin_url': 'https://www.linkedin.com/in/kallelehtinen', 'first_name': 'Kalle', 'last_name': 'Lehtinen', 'company': 'Fortum', 'output': {'number': 1234}}, 'is_async': None}
"""


class NumberSearch(WorkerBase):

    def run(self):
        payload = self.task.get_payload()
        output = self.task.data.get('output', {})

        if output.get('number') and len(output.get('number')) > 5:
            self.context.log.info(f"Found number in output: {output.get('number')}")
            database1 = Database1()
            result = database1.database1_update('Contacts', {'Mobile': output.get('number')}, self.task.data.get('id_zoho'))
            self.context.log.info(f"Database1 update result: {result}")
        else:
            self.context.log.info(f"No number found in output")
            # result = execute_in_process(
            #     process_short_number,
            #     run_config={'ops': {'process_short_number': {'config': {'number': number}}}},
            # )
            # # Handle the result of the sub-graph execution
            # self.context.log.info(f"Sub-graph execution result: {result.success}")

        self.context.log.info(f"Running number search for {payload}")
        return 'Task completed successfully '+json.dumps(payload)


