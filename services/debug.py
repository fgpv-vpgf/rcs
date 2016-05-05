from flask import current_app, Response
from flask.ext.restful import Resource
import db, json


class FetchFile(Resource):

    def get(self, index=None):
        if self.file_param not in current_app.config:
            return 'Parameter {} is not enabled'.format(self.file_param), 404
        lookup_file = current_app.config[self.file_param]
        if index:
            lookup_file += '.{}'.format(index)
        with open(lookup_file) as logfile:
            return Response(logfile.read(), status=200, mimetype='text/plain')


class AccessLog(FetchFile):

    def __init__(self):
        super(AccessLog, self).__init__()
        self.file_param = 'ACCESS_LOG'


class Log(FetchFile):

    def __init__(self):
        super(Log, self).__init__()
        self.file_param = 'LOG_FILE'


class AllKeys(Resource):

    def get(self, lang):
        doc = db.get_all(lang)
        if doc is None:
            return None, 404
        return Response(json.dumps(doc), mimetype='application/json')
