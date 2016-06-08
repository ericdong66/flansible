from datetime import datetime
from flask import render_template
from celery import Celery
import subprocess
import time
from flask_restful import Resource, Api
from ConfigParser import SafeConfigParser
from flask import Flask, request, render_template, session, flash, redirect, url_for, jsonify
from celery import Celery
import subprocess
import time
from flask_restful import Resource, Api, reqparse
from flask_restful_swagger import swagger
import sys
from ModelClasses import AnsibleCommandModel, AnsibleRequestResultModel

app = Flask(__name__)


config = SafeConfigParser()
config.read('config.ini')

app.config['CELERY_BROKER_URL'] = config.get("Default", "CELERY_BROKER_URL")
app.config['CELERY_RESULT_BACKEND'] = config.get("Default", "CELERY_RESULT_BACKEND")

api = swagger.docs(Api(app), apiVersion='0.1')

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)



class StartTask(Resource):
    def get(self):
        task_result = do_long_running_task.apply_async()
        result = {'task_id': task_result.id}
        return result

api.add_resource(StartTask, '/api/starttask')

class RunAnsibleCommand(Resource):
    @swagger.operation(
        notes='Run ad-hoc Ansible command',
        responseClass=AnsibleRequestResultModel.__name__,
        parameters=[
            {
              "name": "body",
              "description": "Inut object",
              "required": True,
              "allowMultiple": False,
              "dataType": AnsibleCommandModel.__name__,
              "paramType": "body"
            }
          ],
        responseMessages=[
            {
              "code": 201,
              "message": "Created. The URL of the created blueprint should be in the Location header"
            },
            {
              "code": 405,
              "message": "Invalid input"
            }
          ]
    )
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('module', type=str, help='module name', required=True)
        args = parser.parse_args()
        req_module = args['module']
        command = str.format("ansible -m {0} localhost", req_module)
        task_result = do_long_running_task.apply_async([command])
        result = {'task_id': task_result.id}
        return result

api.add_resource(RunAnsibleCommand, '/ansiblecommand')


class AnsibleTaskStatus(Resource):
    def get(self, task_id):
        task = do_long_running_task.AsyncResult(task_id)
        result = task.info['result']
        #result_out = task.info.replace('\n', "<br>")
        return result


api.add_resource(AnsibleTaskStatus, '/ansibletaskstatus/<string:task_id>')

@celery.task(bind=True)
def do_long_running_task(self, cmd):
    with app.app_context():
        error_out = None
        result = None
        self.update_state(state='PROGRESS',
                          meta={'result': result})
        try:
            result = subprocess.check_output([cmd], shell=True, stderr=error_out)
        except Exception as e:
            error_out = str(e)

        self.update_state(state='FINISHED',
                          meta={'result': error_out})
        if error_out:
            #failure
            self.update_state(state='FAILED',
                          meta={'result': error_out})
            return {'result': error_out}
        else:
            return {'result': result}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', use_reloader=False)