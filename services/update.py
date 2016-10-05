import regparse, db, json

from flask import Response, current_app
from flask.ext.restful import request, Resource


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
            return Response(json.dumps(msg), mimetype='application/json', status=404)

        try:
            payload = json.loads(request.data)
            for x in langs:
                # The generic fields to update
                if "service_url" in payload[x]:
                    dbdata["request"][x]["service_url"] = payload[x]["service_url"]
                if "service_name" in payload[x]:
                    dbdata["request"][x]["service_name"] = payload[x]["service_name"]
                if "metadata" in payload[x]:
                    dbdata["request"][x]["metadata"] = payload[x]["metadata"]
                # If it's a flavour of Esri feature layer...
                if "esriFeature" or "esriImage" or "esriTile" in payload[x]["service_type"]:
                    if "display_field" in payload[x]:
                        dbdata["request"][x]["display_field"] = payload[x]["display_field"]
                # Or an Esri group layer...
                elif payload[x]["service_type"] == "esriMapServer":
                    if "scrape_only" in payload[x]:
                        dbdata["request"][x]["scrape_only"] = payload[x]["scrape_only"]
                    if "recursive" in payload[x]:
                        dbdata["request"][x]["recursive"] = payload[x]["recursive"]
                # Or a WMS layer/service
                elif payload[x]["service_type"] == "ogcWms":
                    if "legend_format" in payload[x]:
                        dbdata["request"][x]["legend_format"] = payload[x]["legend_format"]
                    if "feature_info_format" in payload[x]:
                        dbdata["request"][x]["feature_info_format"] = payload[x]["feature_info_format"]
                    if "scrape_only" in payload[x]:
                        dbdata["request"][x]["scrape_only"] = payload[x]["scrape_only"]
                    if "recursive" in payload[x]:
                        dbdata["request"][x]["recursive"] = payload[x]["recursive"]
            v2_node, v1_node = regparse.make_node(key, dbdata["request"], current_app.config)
            db.put_doc(key, payload[x]["service_type"], dbdata["request"], layer_config=v2_node, v1_config=v1_node)
        except Exception as e:
            msg = {'msg': 'Error: {0}'.format(e.message)}
            return Response(json.dumps(msg), mimetype='application/json', status=400)

        success = {"msg": "Updated", "key": key}
        return Response(json.dumps(success), mimetype='application/json', status=200)
