from __future__ import division, print_function, unicode_literals

import json, pymongo, requests, parser, db

from flask import Flask, Response
from flask.ext.restful import reqparse, request, abort, Api, Resource

client = pymongo.MongoClient()
jsonset = client.jsontest.json

app = Flask(__name__)
api = Api(app)

def get_doc( smallkey ):
    return jsonset.find_one({'smallkey':smallkey})

def make_feature_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('ServiceURL', type=str, required=True, location='json')
    parser.add_argument('ServiceName', type=str, location='json')
    parser.add_argument('DisplayField', type=str, location='json')
    return parser


class Doc(Resource):
    def get(self, lang, smallkey):
        doc = get_doc( smallkey, lang )
        print( doc )
        if doc is None:
            return None,404
        return Response(json.dumps(doc['data']),  mimetype='application/json')

    def put(self, smallkey):
        data = parser.make_feature_node()
        data = make_feature_parser().parse_args()
        print( data )
        get_feature_service( data )
        print( data )
        jsonset.remove( { 'smallkey':smallkey } )
        jsonset.insert( { 'smallkey':smallkey, 'data':data } )
        return smallkey, 201

class Docs(Resource):
    def get(self, lang, smallkeylist):
        keys = [ x.strip() for x in smallkeylist.split(',') ]
        docs = [ get_doc(smallkey,lang)['data'] for smallkey in keys ]
        return Response(json.dumps(docs),  mimetype='application/json')

class Register(Resource):
    def put(self, smallkey):
        data = parser.make_feature_node()
        data = get_feature_parser().parse_args()
        print( data )
        data = parser.get_feature_service( data )
        print( data )
        jsonset.remove( { 'smallkey':smallkey } )
        jsonset.insert( { 'smallkey':smallkey, 'data':data } )
        return smallkey, 201

    def delete(self, smallkey):
        jsonset.remove( { 'smallkey':smallkey } )
        return '', 204


api.add_resource(Doc, '/doc/<string:lang>/<string:smallkey>')
api.add_resource(Docs, '/docs/<string:lang>/<string:smallkeylist>')
api.add_resource(Register, '/register/<string:smallkey>')

if __name__ == '__main__':
    app.run(debug=True)
