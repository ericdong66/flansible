import shutil
import time

from flask import send_file
from flask_restful import Resource
from flask_restful_swagger import swagger
from flansible import api, app, auth, config
from logger import get_logger

logger = get_logger('download_logs')


class DownloadLogs(Resource):
    @swagger.operation(
        notes='download logs from ansible server',
        nickname='download logs',
        responseMessages=[
            {
                "code": 200,
                "message": "successfully downloaded flansible logs"
            },
            {
                "code": 404,
                "message": "fail to archive ansible playbook"
            }
          ]
    )
    @auth.login_required
    def get(self):
        log_files = '/tmp/flansible_logs_{0}'.format(time.strftime("%Y%m%d_%H%M%S"))
        playbook_root = config.get("Default", "playbook_root")
        try:
            shutil.make_archive(log_files, 'zip', playbook_root)
        except Exception as e:
            logger.debug("fail to archive {0}: {1}".format(playbook_root, e.message))
            return "fail to archive log files", 404

        return send_file('{0}.zip'.format(log_files), as_attachment=True)

api.add_resource(DownloadLogs, '/api/download-logs')
