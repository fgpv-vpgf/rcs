from .registration import Register, Refresh
from .upgrade import Upgrade
from .update import Update
from .retrieval import DocV2, DocsV2, Version
from .debug import AccessLog, Log, AllKeys


from flask import Blueprint
from flask.ext.restful import Api


def make_blueprint(app):
    """
    Create a v2 Flask Blueprint
    """
    bp = Blueprint('api_v2', __name__)
    api = Api(bp)
    api.add_resource(Register, '/register/<string:key>')
    api.add_resource(Refresh, '/refresh/<string:arg>', '/refresh/<string:arg>/<int:limit>')
    api.add_resource(DocV2, '/doc/<string:lang>/<string:smallkey>')
    api.add_resource(DocsV2, '/docs/<string:lang>/<string:smallkeylist>')
    api.add_resource(Upgrade, '/upgrade/2.0/<string:key>')
    api.add_resource(Update, '/update/<string:key>')
    api.add_resource(Version, '/version/')
    if app.config.get('DEBUG_ENDPOINTS'):
        api.add_resource(AccessLog, '/accesslog', '/accesslog/<int:index>')
        api.add_resource(Log, '/log', '/log/<int:index>')
        api.add_resource(AllKeys, '/all_keys', '/all_keys/<string:lang>')
    return bp
