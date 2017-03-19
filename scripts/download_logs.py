#!/usr/bin/python
"""
PYTHONPATH=/home/flansible ./scripts/download_logs.py
"""

import argparse
import shutil

from Flansible.client.flansible_client import FlansibleClient


def parse_options():
    parser = argparse.ArgumentParser(prog='download_logs')
    parser.add_argument('-u', '--url', dest='url', default='http://localhost:3000/', help='flansible server url.')
    return parser.parse_args()


def get_client(flansible_server_url):
    return FlansibleClient(flansible_server_url=flansible_server_url)

if __name__ == '__main__':
    args = parse_options()
    client = get_client(args.url)

    res = client.download_logs()
    if res.status_code != 200:
        raise SystemExit('fail to download log files')
    file_name = res.headers.get('Content-Disposition', '').split('=')[-1]
    with open(file_name, 'w') as F:
        shutil.copyfileobj(res.raw, F)
