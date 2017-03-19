import requests
import time

from urlparse import urljoin
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
from logger import get_logger

logger = get_logger('flansible_client')


class FlansibleClientError(Exception):
    pass


class FlansibleTaskStatus(object):
    ERROR = "ERROR"
    PENDING = "PENDING"
    PROGRESS = "PROGRESS"
    SUCCESS = "SUCCESS"
    FLANSIBLE_TASK_FAILURE = "FLANSIBLE_TASK_FAILURE"
    CELERY_FAILURE = "CELERY_FAILURE"
    stable_status = [SUCCESS, FLANSIBLE_TASK_FAILURE, CELERY_FAILURE, ERROR]
    transit_status = [PENDING, PROGRESS, SUCCESS]


class FlansibleTaskOutput(object):
    ERROR = "ERROR"
    PENDING = "PENDING"
    PROGRESS = "PROGRESS"
    SUCCESS = "SUCCESS"
    stable_status = [SUCCESS, ERROR]
    transit_status = [PENDING, PROGRESS, SUCCESS]


class FlansibleClient(object):
    def __init__(self, flansible_server_url, username='admin', password='admin'):
        self.flansible_server_url = flansible_server_url
        self.auth = HTTPBasicAuth(username, password)

    def _do_request(self, method, api, body=None, timeout=30.0, stream=False):
        assert method in ['POST', 'GET']
        url = urljoin(self.flansible_server_url, api)
        try:
            logger.debug("request: {0}: {1}".format(method, url))
            response = requests.request(method, url, json=body, timeout=timeout, stream=stream, auth=self.auth)
            logger.debug("result: {0}: {1}: {2}".format(method, url, response.status_code))
            return response
        except Exception as e:
            logger.debug("request: {0}: {1}, error: {2}".format(method, url, str(e)))
            raise FlansibleClientError(e.message)

    def post_ansible_playbook(self, book_name, book_plays):
        assert book_name and book_plays
        api = "/api/post-ansible-playbook"
        body = {
            "book_name": book_name,
            "book_plays": book_plays
        }
        return self._do_request(method='POST', api=api, body=body)

    def list_ansible_playbooks(self):
        api = "/api/listplaybooks"
        return self._do_request(method='GET', api=api)

    def run_ansible_playbooks(self,
                              playbook,
                              playbook_dir='/home/flansible/playbook',
                              inventory=None,
                              become=True):
        assert playbook
        api = "/api/ansibleplaybook"
        body = {
            "playbook": playbook,
            "playbook_dir": playbook_dir,
            "inventory": inventory,
            "became": become
        }
        return self._do_request(method='POST', api=api, body=body)

    def get_ansible_task_status(self, task_id):
        api = "/api/ansibletaskstatus/{0}".format(task_id)
        return self._do_request(method='GET', api=api)

    def get_ansible_task_output(self, task_id):
        api = "/api/ansibletaskoutput/{0}".format(task_id)
        return self._do_request(method='GET', api=api)

    def wait_ansible_task_status(self, task_id, timeout=180, time_sleep=1):
        assert task_id
        status_json = None
        timeout_time = datetime.now() + timedelta(seconds=timeout)

        while datetime.now() < timeout_time:
            try:
                status_json = self.get_ansible_task_status(task_id=task_id).json()
            except Exception as e:
                logger.debug("fail to get status, error: {0}".format(str(e)))
                time.sleep(time_sleep)

            if status_json['Status'] in FlansibleTaskStatus.stable_status:
                break
            else:
                time.sleep(time_sleep)
        else:
            return {"Status": "no result after {0} second".format(timeout)}

        return self.get_ansible_task_status(task_id=task_id)

    def wait_ansible_task_output(self, task_id, timeout=180, time_sleep=1):
        assert task_id
        output_json = None
        timeout_time = datetime.now() + timedelta(seconds=timeout)

        while datetime.now() < timeout_time:
            try:
                output_json = self.get_ansible_task_output(task_id=task_id).json()
            except Exception as e:
                logger.debug("fail to get output, error: {0}".format(str(e)))
                time.sleep(time_sleep)

            if output_json['Status'] in FlansibleTaskOutput.stable_status:
                break
            else:
                time.sleep(time_sleep)
        else:
            return {"Output": "no result after {0} second".format(timeout)}

        return self.get_ansible_task_output(task_id=task_id)

    def download_logs(self):
        api = "/api/download-logs"
        return self._do_request(method='GET', api=api)
