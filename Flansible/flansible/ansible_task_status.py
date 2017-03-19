from flask_restful import Resource
from flask_restful_swagger import swagger
from flansible import api, app, celery, auth
import celery_runner


class AnsibleTaskStatus(Resource):
    @swagger.operation(
        notes='Get the status of an Ansible task/job',
        nickname='ansibletaskstatus',
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
                'returncode': None
            }, 404
        if task.state == 'PENDING':
            result_obj = {'Status': "PENDING",
                          'description': "Task not found",
                          'returncode': None}
        elif task.state == 'PROGRESS':
            result_obj = {'Status': "PROGRESS",
                          'description': "Task is currently running",
                          'returncode': None}
        else:
            try:
                return_code = task.info['returncode']
                description = task.info['description']
                if return_code is 0:
                    result_obj = {'Status': "SUCCESS", 
                                  'description': description}
                else:
                    result_obj = {'Status': "FLANSIBLE_TASK_FAILURE",
                                  'description': description,
                                  'returncode': return_code}
            except Exception as e:
                result_obj = {'Status': "CELERY_FAILURE: %s" % str(e)}

        return result_obj, 200

api.add_resource(AnsibleTaskStatus, '/api/ansibletaskstatus/<string:task_id>')
