import os
import json
import yaml

from flask_restful import Resource
from flask_restful import reqparse
from flask_restful_swagger import swagger
from flansible import api, app, auth, config
from ModelClasses import PostAnsiblePlaybookModel, AnsibleRequestResultModel
from logger import get_logger

logger = get_logger('post_ansible_playbook')

ALLOWED_EXTENSIONS = ['yml', 'yaml']


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def data_validator(data):
    try:
        return json.loads(data)
    except ValueError as e:
        logger.debug("fail to load data: {0}, error: {1}".format(data, str(e)))
        return None


class PostAnsiblePlaybook(Resource):
    @swagger.operation(
        notes='post ansible playbook to ansible server',
        nickname='post playbook',
        parameters=[
            {
                "name": "body",
                "description": "input object",
                "required": True,
                "allowMultiple": False,
                "dataType": PostAnsiblePlaybookModel.__name__,
                "paramType": "body"
            }
          ],
        responseMessages=[
            {
                "code": 201,
                "message": "Ansible playbook uploaded"
            },
            {
                "code": 400,
                "message": "fail to upload ansible playbook"
            }
          ]
    )
    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('book_name', type=str, help='playbook name', required=True)
        parser.add_argument('book_plays', type=str, help='playbook content', required=True)
        req_args = parser.parse_args()
        book_name = req_args['book_name']
        book_plays = req_args['book_plays']

        if not book_plays:
            result = "playbook content is empty"
            logger.debug(result)
            return result, 400

        if not allowed_file(book_name):
            result = "playbook name no valid"
            logger.debug(result)
            return result, 400

        playbook_root = config.get("Default", "playbook_root")
        logger.debug("playbook {0} will be saved to {1}".format(book_name, playbook_root))

        valid_data = data_validator(book_plays)
        if valid_data is None:
            return "can not convert string to yaml format", 400

        with open(os.path.join(playbook_root, book_name), "w") as F:
            yaml.safe_dump(valid_data, F, default_flow_style=False)
            logger.debug("saved {0} to playbook {1} in dir {2}".format(book_plays, book_name, playbook_root))

        return "playbook uploaded", 201

api.add_resource(PostAnsiblePlaybook, '/api/post-ansible-playbook')
