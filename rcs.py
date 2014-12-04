"""
The starter module for RCS.  Currently it contains most of the functional code
for RCS and this should eventually end up in separate modules or packages.
"""
from __future__ import division, print_function, unicode_literals

import json, pycouchdb, requests, jsonschema, regparse, db, config, os, logging

from functools import wraps
from logging.handlers import RotatingFileHandler
from flask import Flask, Response, current_app, got_request_exception
from flask.ext.restful import reqparse, request, abort, Api, Resource

app = Flask(__name__)
app.config.from_object(config)
if os.environ.get('RCS_CONFIG'):
    app.config.from_envvar('RCS_CONFIG')
handler = RotatingFileHandler( app.config['LOG_FILE'], maxBytes=10000, backupCount=1 )
handler.setLevel( app.config['LOG_LEVEL'] )
app.logger.addHandler(handler)
api = Api(app)

client = pycouchdb.Server( app.config['DB_CONN'] )
jsonset = client.database( app.config['STORAGE_DB'] )
# client[app.config['DB_NAME']].authenticate( app.config['DB_USER'], app.config['DB_PASS'] )
validator = jsonschema.validators.Draft4Validator( json.load(open(app.config['REG_SCHEMA'])) )

def log_exception(sender,exception):
    """
    Detailed error logging function.  Designed to attach to Flask exception
    events and logs a bit of extra infomration about the request that triggered
    the exception.

    :param sender: The sender for the exception (we don't use this and log everyhing against app right now)
    :param exception: The exception that was triggered
    :type exception: Exception
    """
    app.logger.error(
        """
Request:   {method} {path}
IP:        {ip}
Raw Agent: {agent}
        """.format(
            method = request.method,
            path = request.path,
            ip = request.remote_addr,
            agent = request.user_agent.string,
        ), exc_info=exception
    )
got_request_exception.connect(log_exception, app)

def jsonp(func):
    """
    A decorator function that wraps JSONified output for JSONP requests.
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function

def make_id( key, lang ):
    """
    Generates an RCS ID in the form rcs.a82d987e.en

    :param key: The key to use for generating the unique id (keys are shared amongst different languages)
    :type key: str
    :param lang: The two letter language code for generating the unique id
    :type lang: str
    :returns: str -- an id that should be unique amongst all RCS ids
    """
    return "{0}.{1}.{2}".format('rcs',key,lang)


def get_doc( key, lang ):
    """
    Fetch a record from the document store and output a RAMP compatible configuration.

    :param key: The key to search the document store for
    :type key: str
    :param lang: A two letter language code identifying the language for the response
    :type lang: str
    :returns: dict -- A dictionary representing a JSON configuration fragment for RAMP; None -- key not found
    """
    try:
        o = jsonset.get(key)
    except pycouchdb.exceptions.NotFound as nfe:
        return None
    if o is not None:
        fragment = o.get('data',{}).get(lang,None)
        if fragment is not None:
            result = { 'layers': {} }
            result['layers'][ o['type'] ] = [ fragment ]
            return result
    return None

class Doc(Resource):
    """
    Container class for all web requests for single documents
    """
    @jsonp
    def get(self, lang, smallkey):
        """
        A REST endpoint for fetching a single document from the doc store.

        :param lang: A two letter language code for the response
        :param smallkey: A short key which uniquely identifies the dataset
        :type smallkey: str
        :returns: Response -- a JSON response object; None with a 404 code if the key was not matched
        """
        doc = get_doc( smallkey, lang )
        print( doc )
        if doc is None:
            return None,404
        return Response(json.dumps(doc),  mimetype='application/json')

class Docs(Resource):
    """
    Container class for all web requests for sets of documents
    """
    @jsonp
    def get(self, lang, smallkeylist):
        """
        A REST endpoint for fetching a single document from the doc store.

        :param lang: A two letter language code for the response
        :type lang: str
        :param smallkeylist: A comma separated string of short keys each of which identifies a single dataset
        :type smallkeylist: str
        :returns: list -- an array of JSON configuration fragments (empty error objects are added where keys do not match)
        """
        keys = [ x.strip() for x in smallkeylist.split(',') ]
        docs = [ get_doc(smallkey,lang) for smallkey in keys ]
        print( docs )
        return Response(json.dumps(docs),  mimetype='application/json')

class Register(Resource):
    """
    Container class for all catalog requests for registering new features
    """

    def put(self, smallkey):
        """
        A REST endpoint for adding or editing a single layer.
        All registration requests must contain entries for all languages and will be validated against a JSON schema.

        :param smallkey: A unique identifier for the dataset (can be any unique string, but preferably should be short)
        :type smallkey: str
        :returns: JSON Response -- 201 on success; 400 with JSON payload of an errors array on failure
        """
        try:
            s = json.loads( request.data )
        except Exception:
            return '{"errors":["Unparsable json"]}',400
        if not validator.is_valid( s ):
            resp = { 'errors': [x.message for x in validator.iter_errors(s)] }
            print( resp )
            return Response(json.dumps(resp),  mimetype='application/json', status=400)

        data = dict( key=smallkey )
        if s['payload_type'] == 'wms':
            data['en'] = regparse.wms.make_node( s['en'], make_id(smallkey,'en') )
            data['fr'] = regparse.wms.make_node( s['fr'], make_id(smallkey,'fr') )
        else:
            data['en'] = regparse.esri_feature.make_node( s['en'], make_id(smallkey,'en') )
            data['fr'] = regparse.esri_feature.make_node( s['fr'], make_id(smallkey,'fr') )

        print( data )
        try:
            jsonset.delete( smallkey )
        except pycouchdb.exceptions.NotFound as nfe:
            pass
        jsonset.save( { '_id':smallkey, 'type':s['payload_type'], 'data':data } )
        app.logger.info( 'added a smallkey %s' % smallkey )
        return smallkey, 201

    def delete(self, smallkey):
        """
        A REST endpoint for removing a layer.

        :param smallkey: A unique identifier for the dataset
        :type smallkey: str
        :returns: JSON Response -- 204 on success; 500 on failure
        """
# FIXME send a proper error on missing key
        jsonset.remove( smallkey )
        app.logger.info( 'removed a smallkey %s' % smallkey )
        return '', 204


api.add_resource(Doc, '/doc/<string:lang>/<string:smallkey>')
api.add_resource(Docs, '/docs/<string:lang>/<string:smallkeylist>')
api.add_resource(Register, '/register/<string:smallkey>')

if __name__ == '__main__':
    app.run(debug=True)
