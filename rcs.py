from __future__ import division, print_function, unicode_literals

import json, pymongo, requests, jsonschema, regparse, db, config, os

from functools import wraps
from flask import Flask, Response, current_app
from flask.ext.restful import reqparse, request, abort, Api, Resource

app = Flask(__name__)
app.config.from_object(config)
if os.environ.get('RCS_CONFIG'):
    app.config.from_envvar('RCS_CONFIG')
api = Api(app)

client = pymongo.MongoClient( host=app.config['DB_HOST'], port=app.config['DB_PORT'] )
jsonset = client[app.config['DB_NAME']].json
client[app.config['DB_NAME']].authenticate( app.config['DB_USER'], app.config['DB_PASS'] )
validator = jsonschema.validators.Draft4Validator( json.load(open(app.config['REG_SCHEMA'])) )

def jsonp(func):
    """Wraps JSONified output for JSONP requests."""
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

def get_doc( smallkey, lang ):
    o = jsonset.find_one({'key':smallkey})
    if o is not None:
        fragment = o.get('data',{}).get(lang,None)
        if fragment is not None:
            result = { 'layers': {} }
            result['layers'][ o['type'] ] = [ fragment ]
            return result
    return None

class Doc(Resource):
    def get(self, lang, smallkey):
        doc = get_doc( smallkey, lang )
        print( doc )
        if doc is None:
            return None,404
        return Response(json.dumps(doc),  mimetype='application/json')

class Docs(Resource):
    @jsonp
    def get(self, lang, smallkeylist):
        keys = [ x.strip() for x in smallkeylist.split(',') ]
        docs = [ get_doc(smallkey,lang) for smallkey in keys ]
        print( docs )
        return Response(json.dumps(docs),  mimetype='application/json')

class Register(Resource):
    def put(self, smallkey):
        try:
            s = json.loads( request.data )
        except Exception:
            return '{"errors":["Unparsable json"]}',400
        if not validator.is_valid( s ):
            return Response(json.dumps({ 'errors': [x.message for x in validator.iter_errors(s)] }),  mimetype='application/json'), 400

        data = dict( key=smallkey )
        if s['payload_type'] == 'wms':
            data['en'] = regparse.wms.make_node( s['en'] )
            data['fr'] = regparse.wms.make_node( s['fr'] )
        else:
            data['en'] = regparse.esri_feature.make_node( s['en'] )
            data['fr'] = regparse.esri_feature.make_node( s['fr'] )

        print( data )
        jsonset.remove( { 'key':smallkey } )
        jsonset.insert( { 'key':smallkey, 'type':s['payload_type'], 'data':data } )
        return smallkey, 201

    def delete(self, smallkey):
        jsonset.remove( { 'key':smallkey } )
        return '', 204


api.add_resource(Doc, '/doc/<string:lang>/<string:smallkey>')
api.add_resource(Docs, '/docs/<string:lang>/<string:smallkeylist>')
api.add_resource(Register, '/register/<string:smallkey>')

if __name__ == '__main__':
    app.run(debug=True)
