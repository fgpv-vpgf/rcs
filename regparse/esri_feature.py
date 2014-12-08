"""
An ESRI feature "parser" (really the  requests library does most of the actual parsing).

Most of the utility functions are exposed but most applications won't use them
:func:make_node is generally the only point of interest here.
"""
import requests

def make_grid_col( **kw ):
    """
    Generate a RAMP compliant datagrid column object with the following defaults:
        fieldName ''
        isSortable False
        sortType 'string'
        alignment 0

    :param kw: Takes keyword arguments and just fills in the defaults
    :returns: dict -- a dictionary with the defaults applied
    """
    d = dict( fieldName='', isSortable=False, sortType='string', alignment=0 )
    d.update(kw)
    return d

def make_extent( json_data ):
    """
    Extracts the extent for the layer from ESRI's JSON config.

    :param json_data: A dictionary containing scraped data from an ESRI feature service endpoint
    :type json_data: dict
    :returns: dict -- A dictionary with the same data as the ESRI layerExtent node
    """
    return json_data['extent']

def make_data_grid( json_data ):
    """
    Generate a RAMP datagrid by walking through the attributes.
    Iterates over all entries in *fields* that do not have a type of *esriFieldGeometry*

    :param json_data: A dictionary containing scraped data from an ESRI feature service endpoint
    :type json_data: dict
    :returns: dict -- A dictionary with a single entry *gridColumns* containing an array of datagrid objects
    """
    g = []
    g.append( make_grid_col(id="iconCol", width="50px", title="Icon", columnTemplate="graphic_icon") )
    g.append( make_grid_col(id="detailsCol", width="60px", title="Details", columnTemplate="details_button") )
    g.extend( [ make_grid_col(id=attrib['name'], fieldName=attrib['name'], width="400px",
                              isSortable=True, alignment=1, title=attrib['name'],
                              columnTemplate="unformatted_grid_value") 
                for attrib in json_data['fields'] if attrib['type'] != 'esriFieldGeometry' ] )
    return { 'gridColumns':g }

def get_legend_url( feature_service_url ):
    """
    Converts a feature service URL into a legend request.  Handles the optional '/' at the end of requests.
    
    :param feature_service_url: A URL pointing to an ESRI feature service
    :type feature_service_url: str
    :returns: str -- A URL pointing to a legend request
    """
    if feature_service_url.endswith('/'):
        feature_service_url = feature_service_url[:-1]
    return feature_service_url[:feature_service_url.rfind('/')] + '/legend?f=json'

def get_legend_mapping( data, layer_id ):
    """
    Generates a mapping of layer labels to image data URLs.

    :param data: The initial payload to RCS (should contain a 'service_url' entry)
    :type data: dict
    :param layer_id: The id of the layer to create the mapping for.
    :returns: dict -- a mapping of 'label' => 'data URI encoded image'
    """
    legend_json = requests.get( get_legend_url( data['service_url'] ) ).json()
    for layer in legend_json['layers']:
        if layer['layerId'] == layer_id:
            break
    return { x['label']:'data:'+x['contentType']+';base64,'+x['imageData'] for x in layer['legend'] }

def make_symbology( json_data, data ):
    """
    Generates a symbology node for the RAMP configuration.  Handles simple,
    unique value and class break renders; prefetches all symbology images.

    :param json_data: A dictionary containing scraped data from an ESRI feature service endpoint
    :type json_data: dict
    :param data: The initial payload to RCS (should contain a 'service_url' entry)
    :type data: dict
    :returns: dict -- a symbology node
    """
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

def make_node( data, id ):
    """
    Generate a RAMP layer entry for an ESRI feature service.

    :param data: The initial payload to RCS (should contain a 'service_url' entry)
    :type data: dict
    :param id: An identifier for the layer (as this is unique it is generally supplied from :module:rcs )
    :type id: str
    :returns: dict -- a RAMP configuration fragment representing the ESRI layer
    """
    node = { 'id': id }
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
    node['layerExtent'] = make_extent( svc_data )
    node['symbology'] = make_symbology( svc_data, data )
    return node

