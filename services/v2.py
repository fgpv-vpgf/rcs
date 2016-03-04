from registration import Register
from retrieval import DocV2, DocsV2

from flask import Blueprint
from flask.ext.restful import Api


def make_blueprint():
    """
    Create a v2 Flask Blueprint
    """
    bp = Blueprint('api_v2', __name__)
    api = Api(bp)
    api.add_resource(Register, '/register/<string:key>')
    api.add_resource(DocV2, '/doc/<string:lang>/<string:smallkey>')
    api.add_resource(DocsV2, '/docs/<string:lang>/<string:smallkeylist>')
    return bp
