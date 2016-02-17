"""
The starter module for RCS.  Currently it contains most of the functional code
for RCS and this should eventually end up in separate modules or packages.
"""
from __future__ import division, print_function, unicode_literals

import json, jsonschema, config, os, sys, logging, flask
from services import db, v1

from logging.handlers import RotatingFileHandler
from flask import Flask
from flask.ext.restful import request

# FIXME clean this up
app = Flask(__name__)
reload(sys)
sys.setdefaultencoding('utf8')
app.config.from_object(config)
if os.environ.get('RCS_CONFIG'):
    app.config.from_envvar('RCS_CONFIG')
handler = RotatingFileHandler(app.config['LOG_FILE'],
                              maxBytes=app.config.get('LOG_ROTATE_BYTES', 200000),
                              backupCount=app.config.get('LOG_BACKUPS', 5))
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))

loggers = [app.logger, logging.getLogger('regparse.sigcheck')]
for l in loggers:
    l.setLevel(app.config['LOG_LEVEL'])
    l.addHandler(handler)

flask.got_request_exception.connect(v1.log_exception, app)
if 'ACCESS_LOG' in app.config:
    acc_log = logging.getLogger('testlog')
    acc_log.setLevel(logging.DEBUG)
    acc_handler = RotatingFileHandler(app.config['ACCESS_LOG'],
                                      maxBytes=app.config.get('LOG_ROTATE_BYTES', 200000),
                                      backupCount=app.config.get('LOG_BACKUPS', 5))
    acc_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s '))
    acc_log.addHandler(acc_handler)

    def log_request(sender):
        acc_log.info('{ip} {method} {path} {agent}'.format(method=request.method,
                                                           path=request.path,
                                                           ip=request.remote_addr,
                                                           agent=request.user_agent.string))
        acc_log.debug(request.data)
    flask.request_started.connect(log_request, app)

    def log_response(sender, response):
        acc_log.info('{code} {text}'.format(code=response.status_code, text=response.status))
    flask.request_finished.connect(log_response, app)

db.init_auth_db(app.config['DB_CONN'], app.config['AUTH_DB'])
db.init_doc_db(app.config['DB_CONN'], app.config['STORAGE_DB'])
# client[app.config['DB_NAME']].authenticate( app.config['DB_USER'], app.config['DB_PASS'] )
schema_path = app.config['REG_SCHEMA']
if not os.path.exists(schema_path):
    schema_path = os.path.join(sys.prefix, schema_path)
validator = jsonschema.validators.Draft4Validator(json.load(open(schema_path)))

global_prefix = app.config.get('URL_PREFIX', '')
api_v1_bp = v1.make_v1_blueprint(validator)
app.register_blueprint(api_v1_bp, url_prefix=global_prefix + '/v1')

if __name__ == '__main__':
    for l in loggers:
        l.info('logger started')
    host = '127.0.0.1'
    if '--listen-all' in sys.argv[1:]:
        host = '0.0.0.0'
    app.run(debug=True, host=host)
