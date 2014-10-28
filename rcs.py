from __future__ import division, print_function, unicode_literals

import json, pymongo, requests

from flask import Flask, Response
from flask.ext.restful import reqparse, request, abort, Api, Resource

client = pymongo.MongoClient()
jsonset = client.jsontest.json

app = Flask(__name__)
api = Api(app)

def get_doc( smallkey ):
    return jsonset.find_one({'smallkey':smallkey})

def make_feature_node():
    return dict( boundingBoxVisible=False, layerVisible=True, detailTemplate='default_feature_details',
                 settings={"enabled": True, "opacity": {"enabled": True, "default": 1.0}},
                 mapTipSettings={"hoverTemplate": "feature_hover_maptip_template", "anchorTemplate": "anchored_map_tip"},
                 filter={}, layerAttributes='*' )

def make_grid_col( **kw ):
    d = dict( fieldName='', isSortable=False, sortType='string', alignment=0 )
    d.update(kw)
    return d

def make_data_grid( json_data ):
    datagrid = { "rowsPerPage": 50, "summaryRowTemplate": "default_grid_summary_row" }
    g = []
    g.append( make_grid_col(id="iconCol", width="50px", title="Icon", columnTemplate="graphic_icon") )
    g.append( make_grid_col(id="detailsCol", width="60px", title="Details", columnTemplate="details_button") )
    g.extend( [ make_grid_col(id=attrib['name'], fieldName=attrib['name'], width="400px",
                              isSortable=True, alignment=1, title=attrib['name'],
                              columnTemplate="unformatted_grid_value") 
                for attrib in json_data['fields'] if attrib['type'] != 'esriFieldGeometry' ] )
    datagrid['gridColumns'] = g
    return datagrid

def get_feature_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('ServiceURL', type=str, required=True, location='json')
    parser.add_argument('ServiceName', type=str, location='json')
    parser.add_argument('DisplayField', type=str, location='json')
    return parser

def get_legend_url( feature_service_url ):
    if feature_service_url.endswith('/'):
        feature_service_url = feature_service_url[:-1]
    return feature_service_url[:feature_service_url.rfind('/')] + '/legend?f=json'

def get_legend_mapping( data, layer_id ):
    legend_json = requests.get( get_legend_url( data['ServiceURL'] ) ).json()
    for layer in legend_json['layers']:
        if layer['layerId'] == layer_id:
            break
    return { x['label']:x['url'] for x in layer['legend'] }

def get_feature_service( data ):
    r = requests.get( data['ServiceURL'] + '?f=json' )
    svc_data = r.json()
    print( svc_data  )
    print( svc_data['displayField'] )
    if data['ServiceName'] is None:
        data['ServiceName'] = svc_data['name']
    if data['DisplayField'] is None:
        data['DisplayField'] = svc_data['displayField']
    data['datagrid'] = make_data_grid( svc_data )
    data['symbology'] = make_symbology( svc_data, data )
    return ''

def make_symbology( json_data, data ):
    images_url_prefix = data['ServiceURL'] + '/images/'
    render_json = json_data['drawingInfo']['renderer']
    symb = { 'type':render_json['type'] }
    label_map = get_legend_mapping( data, json_data['id'] )

    if render_json['type'] == 'simple':
        symb['imageUrl'] = images_url_prefix + label_map[render_json['label']]

    elif render_json['type'] == 'uniqueValue':
        if render_json['defaultLabel']:
            symb['defaultImageUrl'] = images_url_prefix + label_map[render_json['defaultLabel']]
        for field in 'field1 field2 field3'.split():
            symb[field] = render_json[field]
        val_maps = [ dict( value= u['value'], imageUrl= images_url_prefix+label_map[u['label']] )
                     for u in render_json['uniqueValueInfos'] ]
        symb['valueMaps'] = val_maps

    elif render_json['type'] == 'classBreaks':
        symb['defaultImageUrl'] = ''
        if json_data['currentVersion'] >= 10.1:
            default_symbol = render_json['url']
            if default_symbol is not None:
                symb['defaultImageUrl'] = get_sym_url()
        symb['field'] = render_json['field']
        symb['minValue'] = render_json['minValue']
        range_maps = [ dict(maxValue=u['classMaxValue'], imageUrl=images_url_prefix+label_map[u['label']])
                       for u in render_json['classBreakInfos'] ]
        symb['valueMaps'] = range_maps
    return symb


class Doc(Resource):
    def get(self, smallkey):
        doc = get_doc( smallkey )
        print( doc )
        if doc is None:
            return None,404
        return Response(json.dumps(doc['data']),  mimetype='application/json')

    def put(self, smallkey):
        data = make_feature_node()
        data = get_feature_parser().parse_args()
        print( data )
        get_feature_service( data )
        print( data )
        jsonset.remove( { 'smallkey':smallkey } )
        jsonset.insert( { 'smallkey':smallkey, 'data':data } )
        return smallkey, 201

class Docs(Resource):
    def get(self, smallkeylist):
        keys = [ x.strip() for x in smallkeylist.split(',') ]
        docs = [ get_doc(smallkey)['data'] for smallkey in keys ]
        return Response(json.dumps(docs),  mimetype='application/json')

api.add_resource(Doc, '/doc/<string:smallkey>')
api.add_resource(Docs, '/docs/<string:smallkeylist>')

if __name__ == '__main__':
    app.run(debug=True)
