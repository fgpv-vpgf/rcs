import requests

def make_feature_node():
    return dict()

def make_grid_col( **kw ):
    d = dict( fieldName='', isSortable=False, sortType='string', alignment=0 )
    d.update(kw)
    return d

def make_data_grid( json_data ):
    g = []
    g.append( make_grid_col(id="iconCol", width="50px", title="Icon", columnTemplate="graphic_icon") )
    g.append( make_grid_col(id="detailsCol", width="60px", title="Details", columnTemplate="details_button") )
    g.extend( [ make_grid_col(id=attrib['name'], fieldName=attrib['name'], width="400px",
                              isSortable=True, alignment=1, title=attrib['name'],
                              columnTemplate="unformatted_grid_value") 
                for attrib in json_data['fields'] if attrib['type'] != 'esriFieldGeometry' ] )
    return { 'gridColumns':g }

def get_legend_url( feature_service_url ):
    if feature_service_url.endswith('/'):
        feature_service_url = feature_service_url[:-1]
    return feature_service_url[:feature_service_url.rfind('/')] + '/legend?f=json'

def get_legend_mapping( data, layer_id ):
    legend_json = requests.get( get_legend_url( data['service_url'] ) ).json()
    for layer in legend_json['layers']:
        if layer['layerId'] == layer_id:
            break
    return { x['label']:'data:'+x['contentType']+';base64,'+x['imageData'] for x in layer['legend'] }

def make_symbology( json_data, data ):
    images_url_prefix = data['service_url'] + '/images/'
    render_json = json_data['drawingInfo']['renderer']
    symb = { 'type':render_json['type'] }
    label_map = get_legend_mapping( data, json_data['id'] )

    if render_json['type'] == 'simple':
        symb['imageUrl'] = label_map[render_json['label']]

    elif render_json['type'] == 'uniqueValue':
        if render_json.get('defaultLabel',None):
            symb['defaultImageUrl'] = label_map[render_json['defaultLabel']]
        for field in 'field1 field2 field3'.split():
            symb[field] = render_json[field]
        val_maps = [ dict( value= u['value'], imageUrl= label_map[u['label']] )
                     for u in render_json['uniqueValueInfos'] ]
        symb['valueMaps'] = val_maps

    elif render_json['type'] == 'classBreaks':
        if render_json.get('defaultLabel',None):
            symb['defaultImageUrl'] = label_map[render_json['defaultLabel']]
        symb['field'] = render_json['field']
        symb['minValue'] = render_json['minValue']
        range_maps = [ dict(maxValue=u['classMaxValue'], imageUrl=label_map[u['label']])
                       for u in render_json['classBreakInfos'] ]
        symb['rangeMaps'] = range_maps
    return symb

def make_node( data ):
    node = make_feature_node()
    r = requests.get( data['service_url'] + '?f=json' )
    svc_data = r.json()
    print( svc_data  )
    print( svc_data['displayField'] )
    node['url'] = data['service_url']
    if data.get('service_name',None) is None:
        node['displayName'] = svc_data['name']
    if data.get('display_field',None) is None:
        node['nameField'] = svc_data['displayField']
    node['datagrid'] = make_data_grid( svc_data )
    node['symbology'] = make_symbology( svc_data, data )
    return node

