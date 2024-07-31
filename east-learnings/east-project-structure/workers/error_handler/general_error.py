import datetime

from app.workers.WorkerBase import WorkerBase


class GeneralError(WorkerBase):

    def run(self):
        # write task to file
        path = '/project/dagster/logs/worker-error-'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")+'.json'
        with open(path, 'w') as f:
            f.write(self.task.get_payload())
