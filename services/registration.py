import regparse, db, json, flask, pycouchdb

from flask import Response, current_app
from flask.ext.restful import request, abort, Resource


def get_registration_errors(data):
    """
    Test the schema for validity, return all errors found as a flat list of messages.
    """
    validator = flask.g.get_validator()
    if not validator.is_valid(data):
        return [x.message for x in validator.iter_errors(data)]
    return []


def refresh_records(day_limit, limit, config):
    import datetime, string
    valid = []
    invalid = {}
    query = ""
    if day_limit is None:
        query = "function(doc) { emit(doc._id, { updated: doc.updated_at, version: doc.version, request: doc.data ? doc.data.request : doc.request }); }"  # NOQA
    else:
        min_age = datetime.date.today() - datetime.timedelta(days=day_limit)
        query = "function(doc) { if (doc.updated_at <= '$date') emit(doc._id, { updated: doc.updated_at, version: doc.version, request: doc.data ? doc.data.request : doc.request }); }"  # NOQA
        query = string.Template(query).substitute(date=min_age)
    current_app.logger.debug('CouchDB Query {0}'.format(query))
    results = db.query(query)
    count = 0
    limit_reached = False
    for r in results:
        if limit is not None:
            # annoying count is necessary since we don't want to convert a generator into a list
            count += 1
            if count > limit:
                limit_reached = True
                break

        key = r['id']
        current_app.logger.info('refresh {0}'.format(key))
        if 'request' not in r['value']:
            invalid[key] = 'previous request was not cached (request caching added in 1.8.0)'
            continue
        if r['value'].get('version', None) != '2.0':
            invalid[key] = 'v1 record found; upgrading record types has not yet been implemented'
            continue
        req = r['value']['request']
        try:
            v2_node, v1_node = regparse.make_node(key, req, config)
            db.put_doc(key, v2_node.values()[0]['layerType'], req, layer_config=v2_node, v1_config=v1_node)
            valid.append(key)
        except Exception as e:
            current_app.logger.warning('Error in refresh', exc_info=e)
            invalid[key] = str(e)

    return {"updated": valid, "errors": invalid, 'limit_reached': limit_reached}


class Register(Resource):
    """
    Container class for all catalog requests for registering new features.
    """

    @regparse.sigcheck.validate
    def put(self, key):
        """
        A REST endpoint for adding or editing a single layer.
        All registration requests must contain entries for all languages and will be validated against a JSON schema.

        :param smallkey: A unique identifier for the dataset (can be any unique string, but preferably should be short)
        :type smallkey: str
        :returns: JSON Response -- 201 on success; 400 with JSON payload of an errors array on failure
        """
        try:
            req = json.loads(request.data)
        except Exception as e:
            current_app.logger.error(e.message)
            return '{"errors":["Unparsable json"]}', 400
        errors = get_registration_errors(req)
        if errors:
            resp = {'errors': errors}
            current_app.logger.info(resp)
            return Response(json.dumps(resp), mimetype='application/json', status=400)

        try:
            v2_node, v1_node = regparse.make_node(key, req, current_app.config)
        except regparse.metadata.MetadataException as mde:
            current_app.logger.warning('Metadata could not be retrieved for layer', exc_info=mde)
            abort(400, msg=mde.message)
        except regparse.ServiceEndpointException as se:
            current_app.logger.warning('Problem reading service endpoints', exc_info=se)
            abort(400, msg=se.message)

        current_app.logger.debug(v2_node)
        current_app.logger.debug(v1_node)
        db.put_doc(key, v2_node.values()[0]['layerType'], req, layer_config=v2_node, v1_config=v1_node)
        current_app.logger.info('added a key %s' % key)
        return Response(json.dumps(dict(key=key)), mimetype='application/json', status=201)

    @regparse.sigcheck.validate
    def delete(self, key):
        """
        A REST endpoint for removing a layer.

        :param smallkey: A unique identifier for the dataset
        :type smallkey: str
        :returns: JSON Response -- 204 on success; 500 on failure
        """
        try:
            db.delete_doc(key)
            current_app.logger.info('removed a key %s' % key)
            return '', 204
        except pycouchdb.exceptions.NotFound as nfe:
            current_app.logger.info('key was not found %s' % key, exc_info=nfe)
        return '', 404


class Update(Resource):
    """
    Handles updates to an ESRI feature entry
    """

    @regparse.sigcheck.validate
    def post(self, smallkey):
        """
        A REST endpoint for updating details in a feature layer.

        :param smallkey: A unique identifier for the dataset (can be any unique string, but preferably should be short)
        :type smallkey: str
        :returns: JSON Response -- 200 on success; 400 with JSON payload of an errors array on failure
        """
        try:
            payload = json.loads(request.data)
        except Exception:
            return '{"errors":["Unparsable json"]}', 400

        fragment = {'en': {}, 'fr': {}}
        if len(payload) == 2 and 'en' in payload and 'fr' in payload:
            fragment = payload
        else:
            fragment['en'].update(payload)
            fragment['fr'].update(payload)

        dbdata = db.get_raw(smallkey)

        if dbdata is None:
            return '{"errors":["Record not found in database"]}', 404
        elif dbdata['type'] != 'feature':
            return '{"errors":["Record is not a feature layer"]}', 400

        dbdata['data']['request']['en'].update(fragment['en'])
        dbdata['data']['request']['fr'].update(fragment['fr'])

        errors = get_registration_errors(payload)
        if errors:
            resp = {'errors': errors}
            current_app.logger.info(resp)
            return Response(json.dumps(resp), mimetype='application/json', status=400)

        try:
            data = regparse.make_record(smallkey, dbdata['data']['request'], current_app.config)
        except regparse.metadata.MetadataException as mde:
            current_app.logger.warning('Metadata could not be retrieved for layer', exc_info=mde)
            abort(400, msg=mde.message)

        db.put_doc(smallkey, {'type': data['request']['payload_type'], 'data': data})

        return smallkey, 200


class Refresh(Resource):
    """
    Handles cache maintenance requests
    """

    @regparse.sigcheck.validate
    def post(self, arg, limit=None):
        """
        A REST endpoint for triggering cache updates.
        Walks through the database and updates cached data.

        :param arg: Either 'all' or a positive integer indicating the minimum
        age in days of a record before it should be updated
        :type arg: str
        :returns: JSON Response -- 200 on success; 400 on malformed URL
        """
        day_limit = None
        rec_limit = None

        try:
            day_limit = int(arg)
        except:
            pass
        if day_limit is None and arg != 'all' or day_limit is not None and day_limit < 1:
            return '{"error":"argument should be either \'all\' or a positive integer"}', 400

        if limit is not None:
            try:
                rec_limit = int(limit)
            except:
                return '{"error":"limit must be positive integer if specified"}', 400
        return Response(json.dumps(refresh_records(day_limit, rec_limit, current_app.config)),
                        mimetype='application/json')
