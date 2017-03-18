import requests

from urlparse import urljoin
from requests.auth import HTTPBasicAuth
from logger import get_logger

logger = get_logger('flansible_client')


class FlansibleClientError(Exception):
    pass


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
        api = "/api/post_ansible_playbook"
        body = {
            "book_name": book_name,
            "book_plays": book_plays
        }
        return self._do_request(method='POST', api=api, body=body)

    def list_ansible_playbooks(self):
        api = "/api/listplaybooks"
        return self._do_request(method='GET', api=api)

    def run_ansible_playbooks(self):
        raise NotImplementedError
