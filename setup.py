#!/usr/bin/env python

import setuptools

setuptools.setup(
    name='flansible',
    version="0.3.0",
    license="MIT",
    description='super-duper-simple rest api for ansible tasks',
    packages=['Flansible',
              'Flansible.Examples',
              'Flansible.Utils',
              'Flansible.flansible',
              'Flansible.playbook',
              'Flansible.playbook.templates'
              ],
    include_package_data=True,
    package_data={
        'Flansible': ['*.*'],
        'Flansible.Examples': ['*.*'],
        'Flansible.Utils': ['*.*'],
        'Flansible.flansible': ['*.*'],
        'Flansible.playbook': ['*.*'],
        'Flansible.playbook.templates': ['*.*'],
    },
    install_requires=[
        'celery==4.0.0',
        'Flask==0.10.1',
        'Flask-HTTPAuth==3.1.2',
        'Flask-RESTful==0.3.5',
        'flask-restful-swagger==0.19',
        'flower==0.9.1',
        'redis==2.10.5',
        'scp==0.10.2',
        'paramiko==2.4.0',
        'PyYAML==3.10',
        'httplib2==0.8',
        'requests==2.13.0',
        'lxml==3.7.3',
        'cssselect==1.0.1',
        'xmltodict==0.10.2',
        'pywinrm==0.2.2',
    ],
    entry_points={
        'console_scripts': [
            'flansible = Flansible.playbook:site'
        ]
    }
)
