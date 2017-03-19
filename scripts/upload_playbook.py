#!/usr/bin/python
"""
PYTHONPATH=/home/flansible ./scripts/upload_playbook.py --file /path/to/playbook.yml
"""

import json
import yaml
import argparse
from os.path import basename

from Flansible.client.flansible_client import FlansibleClient


def parse_options():
    parser = argparse.ArgumentParser(prog='upload_playbook')
    parser.add_argument('-u', '--url', dest='url', default='http://localhost:3000/', help='flansible server url.')
    parser.add_argument('-f', '--file', dest='file', required=True, help='playbook file name with full path.')
    return parser.parse_args()


def get_client(flansible_server_url):
    return FlansibleClient(flansible_server_url=flansible_server_url)

if __name__ == '__main__':
    args = parse_options()
    client = get_client(args.url)
    book_name = args.file
    with open(book_name, 'r') as F:
        try:
            book_plays = json.dumps(yaml.load(F))
            res = client.post_ansible_playbook(book_name=book_name, book_plays=book_plays)
            assert res.status_code == 201
        except ValueError:
            raise SystemExit('can not load file as yaml')
        except AssertionError:
            raise SystemExit('fail to upload playbook')

    res = client.list_ansible_playbooks()
    if res.status_code == 200:
        all_playbooks = res.json()
    else:
        raise SystemExit('fail to list ansible playbooks')

    for playbook in all_playbooks:
        if playbook['playbook'] == basename(book_name):
            break
    else:
        raise SystemExit('fail to verify uploaded playbook')
