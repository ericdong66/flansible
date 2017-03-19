#!/usr/bin/python
"""
PYTHONPATH=/home/flansible ./scripts/run_playbook.py --playbook playbook.yml
"""

import argparse

from Flansible.client.flansible_client import FlansibleClient


def parse_options():
    parser = argparse.ArgumentParser(prog='run_playbook')
    parser.add_argument('-u', '--url', dest='url', default='http://localhost:3000/', help='flansible server url.')
    parser.add_argument('-p', '--playbook', dest='playbook', required=True, help='playbook file name with full path.')
    return parser.parse_args()


def get_client(flansible_server_url):
    return FlansibleClient(flansible_server_url=flansible_server_url)

if __name__ == '__main__':
    args = parse_options()
    client = get_client(args.url)
    book_name = args.playbook

    res = client.list_ansible_playbooks()
    if res.status_code == 200:
        all_playbooks = res.json()
    else:
        raise SystemExit('fail to list ansible playbooks')

    for playbook in all_playbooks:
        if playbook['playbook'] == book_name:
            break
    else:
        raise SystemExit('playbook does not exist on server')

    res = client.run_ansible_playbooks(playbook=book_name)
    if res.status_code != 200:
        raise SystemExit('fail to run playbook')

    task_id = res.json()['task_id']
    res = client.get_ansible_task_status(task_id=task_id)
    if res.status_code != 200:
        raise SystemExit('fail to get play status')
    else:
        print res.json()

    res = client.wait_ansible_task_status(task_id=task_id)
    print res.content

    res = client.wait_ansible_task_output(task_id=task_id)
    print res.json()['output']
