from registration import Register

from flask import Blueprint
from flask.ext.restful import Api


def make_blueprint():
    """
    Create a v2 Flask Blueprint
    """
    bp = Blueprint('api_v2', __name__)
    api = Api(bp)
    api.add_resource(Register, '/register/<string:smallkey>')
    return bp
