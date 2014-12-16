"""
The starter module for RCS.  Currently it contains most of the functional code
for RCS and this should eventually end up in separate modules or packages.
"""
from __future__ import division, print_function, unicode_literals

import json, pycouchdb, requests, jsonschema, regparse, db, config, os, sys, logging

from functools import wraps
from logging.handlers import RotatingFileHandler
from flask import Flask, Blueprint, Response, current_app, got_request_exception
from flask.ext.restful import reqparse, request, abort, Api, Resource

# FIXME clean this up
app = Flask(__name__)
app.config.from_object(config)
if os.environ.get('RCS_CONFIG'):
    app.config.from_envvar('RCS_CONFIG')
handler = RotatingFileHandler( app.config['LOG_FILE'], maxBytes=10000, backupCount=1 )
handler.setLevel( app.config['LOG_LEVEL'] )
handler.setFormatter( logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))

loggers = [app.logger, logging.getLogger('regparse.sigcheck')]
for l in loggers:
    l.addHandler( handler )


db.init_auth_db( app.config['DB_CONN'], app.config['AUTH_DB'] )
db.init_doc_db( app.config['DB_CONN'], app.config['STORAGE_DB'] )
# client[app.config['DB_NAME']].authenticate( app.config['DB_USER'], app.config['DB_PASS'] )
schema_path = app.config['REG_SCHEMA']
if not os.path.exists(schema_path):
    schema_path = os.path.join( sys.prefix, schema_path )
validator = jsonschema.validators.Draft4Validator( json.load(open(schema_path)) )

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
        doc = db.get_doc( smallkey, lang, self.version )
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
        docs = [ db.get_doc(smallkey, lang, self.version) for smallkey in keys ]
        print( docs )
        return Response(json.dumps(docs),  mimetype='application/json')

class DocV10(Doc):
    def __init__(self):
        super(DocV10,self).__init__()
        self.version = '1.0'

class DocV11(Doc):
    def __init__(self):
        super(DocV11,self).__init__()
        self.version = '1.1'

class DocsV10(Docs):
    def __init__(self):
        super(DocsV10,self).__init__()
        self.version = '1.0'

class DocsV11(Docs):
    def __init__(self):
        super(DocsV11,self).__init__()
        self.version = '1.1'

class Register(Resource):
    """
    Container class for all catalog requests for registering new features
    """

    @regparse.sigcheck.validate
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
            app.logger.info( resp )
            return Response(json.dumps(resp),  mimetype='application/json', status=400)

        data = dict( key=smallkey )
        try:
            if s['payload_type'] == 'wms':
                data['en'] = regparse.wms.make_node( s['en'], make_id(smallkey,'en'), app.config )
                data['fr'] = regparse.wms.make_node( s['fr'], make_id(smallkey,'fr'), app.config )
            else:
                data['en'] = regparse.esri_feature.make_node( s['en'], make_id(smallkey,'en'), app.config )
                data['fr'] = regparse.esri_feature.make_node( s['fr'], make_id(smallkey,'fr'), app.config )
        except regparse.metadata.MetadataException as mde:
            app.logger.warning( 'Metadata could not be retrieved for layer', exc_info=mde )
            abort( 400, msg=mde.message )

        app.logger.debug( data )

        db.put_doc( smallkey, { 'type':s['payload_type'], 'data':data } )
        app.logger.info( 'added a smallkey %s' % smallkey )
        return smallkey, 201

    @regparse.sigcheck.validate
    def delete(self, smallkey):
        """
        A REST endpoint for removing a layer.

        :param smallkey: A unique identifier for the dataset
        :type smallkey: str
        :returns: JSON Response -- 204 on success; 500 on failure
        """
        # valid_sig = regparse.sigcheck.test_request( request )
# FIXME send a proper error on missing key
        try:
            db.delete_doc( smallkey )
            app.logger.info( 'removed a smallkey %s' % smallkey )
            return '', 204
        except pycouchdb.exceptions.NotFound as nfe:
            app.logger.info( 'smallkey was not found %s' % smallkey,  exc_info=nfe )
        return '',404


api_1_0_bp = Blueprint('api_1_0', __name__, url_prefix='/1.0')
api_1_0 = Api(api_1_0_bp)
api_1_0.add_resource(DocV10, '/doc/<string:lang>/<string:smallkey>')
api_1_0.add_resource(DocsV10, '/docs/<string:lang>/<string:smallkeylist>')
api_1_0.add_resource(Register, '/register/<string:smallkey>')
app.register_blueprint(api_1_0_bp)

api_1_1_bp = Blueprint('api_1_1', __name__, url_prefix='/1.1')
api_1_1 = Api(api_1_1_bp)
api_1_1.add_resource(DocV11, '/doc/<string:lang>/<string:smallkey>')
api_1_1.add_resource(DocsV11, '/docs/<string:lang>/<string:smallkeylist>')
api_1_1.add_resource(Register, '/register/<string:smallkey>')
app.register_blueprint(api_1_1_bp)

if __name__ == '__main__':
    for l in loggers:
        l.setLevel(0)
        l.info( 'logger started' )
    app.run(debug=True)
