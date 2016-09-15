import regparse, db, json

from flask import Response, current_app
from flask.ext.restful import Resource


def wms_upgrade(v1_request):
    steal_fields = ['service_url', 'service_name', 'metadata', 'legend_format']
    result = {x: v1_request[x] for x in steal_fields if x in v1_request}
    result['service_type'] = regparse.ServiceTypes.WMS
    fi_type = v1_request.get('feature_info_type')
    if fi_type in ['text/html;fgpv=summary', 'text/html', 'text/plain', 'application/json']:
        result['feature_info_format'] = fi_type
    result['scrape_only'] = [v1_request['layer']]
    return result


def feat_upgrade(v1_request):
    steal_fields = ['service_url', 'metadata', 'loading_mode', 'max_allowable_offset', 'display_field', 'service_name']
    result = {x: v1_request[x] for x in steal_fields if x in v1_request}
    result['service_type'] = regparse.ServiceTypes.FEATURE
    return result


class Upgrade(Resource):
    """
    Handles upgrading of entries from v1 to v2
    """

    @regparse.sigcheck.validate
    def post(self, key):
        """
        A REST endpoint for upgrading a previous registration from v1 to v2.

        :param key: A unique identifier for the dataset
        :type key: str
        :returns: JSON Response -- 200 on success; 4xx if problems are encountered
        """
        dbdata = db.get_raw(key)

        if dbdata is None:
            return '{"msg":"Record not found in database"}', 404
        elif dbdata.get('version') == '2.0':
            return '{"msg":"Already upgraded"}', 200
        elif dbdata['data'].get('request') is None:
            return '{"msg":"Previous request was not cached (request caching added in 1.8.0)"}', 409

        try:
            v1_request = dbdata['data']['request']
            upgrade_method = wms_upgrade if v1_request['payload_type'] == 'wms' else feat_upgrade
            v2_request = {lang: upgrade_method(v1_request[lang]) for lang in current_app.config['LANGS']}
            print v2_request
            v2_node, v1_node = regparse.make_node(key, v2_request, current_app.config)
            db.put_doc(key, v2_node.values()[0]['layerType'], v2_request, layer_config=v2_node, v1_config=v1_node)
        except Exception as e:
            msg = {'msg': 'Error: {0}'.format(e.message)}
            current_app.logger.error('Failed to upgrade {0}'.format(key), exc_info=e)
            return Response(json.dumps(msg), mimetype='application/json', status=400)

        success = {"msg": "Upgraded", "version": "2.0", "key": key}
        return Response(json.dumps(success), mimetype='application/json', status=200)
