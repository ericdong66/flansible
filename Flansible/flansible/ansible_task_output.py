from flask_restful import Resource, Api
from flask_restful_swagger import swagger
from flansible import app
from flansible import api, app, celery, auth
from ModelClasses import AnsibleCommandModel, AnsiblePlaybookModel, AnsibleRequestResultModel, AnsibleExtraArgsModel
import celery_runner


class AnsibleTaskOutput(Resource):
    @swagger.operation(
        notes='Get the output of an Ansible task/job',
        nickname='ansibletaskoutput',
        parameters=[
            {
                "name": "task_id",
                "description": "The ID of the task/job to get status for",
                "required": True,
                "allowMultiple": False,
                "dataType": 'string',
                "paramType": "path"
            }
        ])
    @auth.login_required
    def get(self, task_id):
        try:
            task = celery_runner.do_long_running_task.AsyncResult(task_id)
        except Exception as e:
            return {
                'Status': "ERROR",
                'description': e.message,
                'returncode': 1
            }, 404
        if task.state == 'PENDING':
            result_obj = {'Status': "PENDING",
                          'description': "Task not found",
                          'output': None,
                          'returncode': None}
        elif task.state == "PROGRESS":
            result_obj = {'Status': "PROGRESS",
                          'description': "Task not found",
                          'output': task.info['output'],
                          'returncode': None}
        else:
            result_obj = {'Status': "SUCCESS",
                          'description': "Task not found",
                          'output': task.info['output'],
                          'returncode': 0}
        return result_obj, 200

api.add_resource(AnsibleTaskOutput, '/api/ansibletaskoutput/<string:task_id>')
