import json, numbers

from . import regparse, db, registration
from .retrieval import DocV1, DocsV1
from flask import Blueprint, Response, current_app
from flask.ext.restful import request, Api, Resource


class Simplification(Resource):
    """
    Handles updates to simplification factor of a feature layer
    """

    @regparse.sigcheck.validate
    def put(self, smallkey):
        """
        A REST endpoint for updating a simplification factor on a registered feature service.

        :param smallkey: A unique identifier for the dataset (can be any unique string, but preferably should be short)
        :type smallkey: str
        :returns: JSON Response -- 200 on success; 400 with JSON payload of an errors array on failure
        """
        try:
            payload = json.loads(request.data)
        except Exception:
            return '{"errors":["Unparsable json"]}', 400

        # Check that our payload has a 'factor' property that contains an integer
        if not isinstance(payload['factor'], numbers.Integral):
            resp = {'errors': ['Invalid payload JSON']}
            current_app.logger.info(resp)
            return Response(json.dumps(resp), mimetype='application/json', status=400)

        intFactor = int(payload['factor'])

        # Grab english and french doc fragments
        dbdata = db.get_raw(smallkey)

        if dbdata is None:
            return '{"errors":["Record not found in database"]}', 404

        elif dbdata['type'] != 'feature':
            return '{"errors":["Record is not a feature layer"]}', 400
        else:
            # Add in new simplification factor
            dbdata['data']['en']['maxAllowableOffset'] = intFactor
            dbdata['data']['fr']['maxAllowableOffset'] = intFactor

            # Also store factor in the request, so we can preserve the factor during an update
            dbdata['data']['request']['en']['max_allowable_offset'] = intFactor
            dbdata['data']['request']['fr']['max_allowable_offset'] = intFactor

        # Update the database record
        db.put_doc(smallkey, {'type': dbdata['type'], 'data': dbdata['data']})

        current_app.logger.info('updated simpification factor on smallkey %(s)s to %(f)d by %(u)s'
                                % {"s": smallkey, "f": intFactor, "u": payload['user']})
        return smallkey, 200


def make_blueprint():
    """
    Create a v1 Flask Blueprint
    """
    api_v1_bp = Blueprint('api_v1', __name__)
    api_1 = Api(api_v1_bp)
    api_1.add_resource(DocV1, '/doc/<string:lang>/<string:smallkey>')
    api_1.add_resource(DocsV1, '/docs/<string:lang>/<string:smallkeylist>',
                       '/docs/<string:lang>/<string:smallkeylist>/<string:sortarg>')

    @api_v1_bp.route('/register/<string:smallkey>', methods=['PUT', 'DELETE'])
    def reg_obsolete(smallkey):
        return Response('{"deprecated":"Registration should be performed using the V2 API"}',
                        mimetype='application/json', status=410)

    api_1.add_resource(registration.Refresh, '/update/<string:arg>')

    @api_v1_bp.route('/simplification/<string:smallkey>', methods=['PUT'])
    def simp_obsolete(smallkey):
        return Response('{"deprecated":"Simplification is deprecated, use the v2 update endpoint to edit entries"}',
                        mimetype='application/json', status=410)

    @api_v1_bp.route('/updatefeature/<string:smallkey>', methods=['PUT', 'DELETE'])
    def uf_obsolete(smallkey):
        return Response('{"deprecated":"Update feature should be performed using the V2 API"}',
                        mimetype='application/json', status=410)

    return api_v1_bp
