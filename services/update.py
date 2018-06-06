import json

from . import regparse, db
from flask import Response, current_app
from flask.ext.restful import request, Resource


class Payload:
    PARAMS = (['service_url', 'service_type', 'service_name', 'metadata', 'display_field',
              'scrape_only', 'recursive', 'legend_format', 'feature_info_format'])


class Update(Resource):
    """
    Updates a specific element of an existing registration
    """

    @regparse.sigcheck.validate
    def put(self, key):
        """
        A REST endpoint for updating one or more nodes of an existing request.

        :param key: A unique identifier for the dataset
        :type key: str
        :returns: JSON Response -- 200 on success; 4xx if problems are encountered
        """

        langs = ["en", "fr"]
        try:
            dbdata = db.get_raw(key)
            if dbdata is None:
                return '{"msg":"Record not found in database"}', 404
        except Exception as e:
            msg = {'msg': 'Error: {0}'.format(e.message)}
            return Response(json.dumps(msg), mimetype='application/json', status=500)

        def replace_if_set(params):
            for p in params:
                if p in payload_seg:
                    request_seg[p] = payload_seg[p]

        try:
            payload = json.loads(request.data)
            for lang in langs:
                request_seg = dbdata['request'][lang]
                payload_seg = payload[lang]
                replace_if_set(Payload.PARAMS)
                v2_node, v1_node = regparse.make_node(key, dbdata["request"], current_app.config)
                db.put_doc(key, request_seg["service_type"], dbdata["request"],
                           layer_config=v2_node, v1_config=v1_node)
        except Exception as e:
            msg = {'msg': 'Error: {0}'.format(e.message)}
            return Response(json.dumps(msg), mimetype='application/json', status=500)
        success = {"msg": "Updated", "key": key}
        return Response(json.dumps(success), mimetype='application/json', status=200)
