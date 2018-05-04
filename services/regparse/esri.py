"""
An ESRI feature "parser" (really the  requests library does most of the actual parsing).

Most of the utility functions are exposed but most applications won't use them
:func:make_node is generally the only point of interest here.
"""
import requests, flask


# TODO test me


def make_grid_col(**kw):
    """
    Generate a RAMP compliant datagrid column object with the following defaults:
        fieldName ''
        isSortable False
        sortType 'string'
        alignment 0

    :param kw: Takes keyword arguments and just fills in the defaults
    :returns: dict -- a dictionary with the defaults applied
    """
    d = {'fieldName': '', 'orderable': False, 'type': 'string', 'alignment': 0}
    d.update(kw)
    return d


def make_extent(json_data):
    """
    Extracts the extent for the layer from ESRI's JSON config.

    :param json_data: A dictionary containing scraped data from an ESRI feature service endpoint
    :type json_data: dict
    :returns: dict -- A dictionary with the same data as the ESRI layerExtent node
    """
    return json_data['extent']


def make_data_grid(json_data):
    """
    Generate a RAMP datagrid by walking through the attributes.
    Iterates over all entries in *fields* that do not have a type of *esriFieldTypeGeometry*

    :param json_data: A dictionary containing scraped data from an ESRI feature service endpoint
    :type json_data: dict
    :returns: dict -- A dictionary with a single entry *gridColumns* containing an array of datagrid objects
    """
    g = []
    g.append(make_grid_col(id="iconCol", width="50px", title="Icon", columnTemplate="graphic_icon"))
    g.append(make_grid_col(id="detailsCol", width="60px", title="Details", columnTemplate="details_button"))
    g.extend([make_grid_col(id=attrib['name'], fieldName=attrib['name'], width="400px",
                            orderable=True, alignment=1, title=attrib['name'],
                            columnTemplate="unformatted_grid_value")
              for attrib in json_data['fields'] if attrib['type'] != 'esriFieldTypeGeometry'])
    return {'gridColumns': g}


def get_base_url(feature_service_url):
    """
    Strips trailing / from the feature service URL if present.

    :param feature_service_url: A URL pointing to an ESRI feature service
    :type feature_service_url: str
    :returns: str -- A URL pointing to the base URL
    """
    if feature_service_url.endswith('/'):
        return feature_service_url[:-1]
    return feature_service_url


def get_legend_url(feature_service_url):
    """
    Converts a feature service URL into a legend request.  Handles the optional '/' at the end of requests.

    :param feature_service_url: A URL pointing to an ESRI feature service
    :type feature_service_url: str
    :returns: str -- A URL pointing to a legend request
    """
    feature_service_url = get_base_url(feature_service_url)
    return feature_service_url[:feature_service_url.rfind('/')] + '/legend?f=json'


def get_legend_mapping(feature_url, layer_id):
    """
    Generates a mapping of layer labels to image data URLs.

    :param feature_url: The service endpoint URL for an ESRI feature layer
    :type feature_url: str
    :param layer_id: The id of the layer to create the mapping for.
    :returns: dict -- a mapping of 'label' => 'data URI encoded image'
    """
    legend_json = requests.get(get_legend_url(feature_url), proxies=flask.g.proxies).json()
    for layer in legend_json['layers']:
        if layer['layerId'] == layer_id:
            break
    return {x['label']: 'data:' + x['contentType'] + ';base64,' + x['imageData'] for x in layer['legend']}


def make_alias_mapping(json_data):
    """
    Generates a mapping of field names to field aliases.

    :param json_data: An array of field objects, taken from the fields property of an ESRI feature service endpoint
    :type json_data: list
    :returns: dict -- a mapping of 'name' => 'alias'
    """
    return {x['name']: x['alias'] for x in json_data}


def make_symbology(json_data, feature_url):
    """
    Generates a symbology node for the RAMP configuration.  Handles simple,
    unique value and class break renders; prefetches all symbology images.

    :param json_data: A dictionary containing scraped data from an ESRI feature service endpoint
    :type json_data: dict
    :param feature_service_url: A URL pointing to an ESRI feature service
    :type feature_url: str
    :returns: dict -- a symbology node
    """
    render_json = json_data['drawingInfo']['renderer']
    symb = {'type': render_json['type']}
    label_map = get_legend_mapping(feature_url, json_data['id'])

    if render_json['type'] == 'simple':
        symb['imageUrl'] = label_map[render_json['label']]
        symb['label'] = render_json['label']

    elif render_json['type'] == 'uniqueValue':
        if render_json.get('defaultLabel', None) and render_json['defaultLabel'] in label_map:
            symb['defaultImageUrl'] = label_map[render_json['defaultLabel']]
            symb['label'] = render_json['defaultLabel']
        for field in 'field1 field2 field3'.split():
            symb[field] = render_json[field]
        val_maps = [dict(value=u['value'], imageUrl=label_map[u['label']], label=u['label'])
                    for u in render_json['uniqueValueInfos']]
        symb['valueMaps'] = val_maps

    elif render_json['type'] == 'classBreaks':
        if render_json.get('defaultLabel', None) and render_json['defaultLabel'] in label_map:
            symb['defaultImageUrl'] = label_map[render_json['defaultLabel']]
            symb['label'] = render_json['defaultLabel']
        symb['field'] = render_json['field']
        symb['minValue'] = render_json['minValue']
        range_maps = [dict(maxValue=u['classMaxValue'], imageUrl=label_map[u['label']], label=u['label'])
                      for u in render_json['classBreakInfos']]
        symb['rangeMaps'] = range_maps
    return symb


def test_small_layer(svc_url, svc_data):
    """
    Test a service endpoint to see if the layer is small based on some simple rules.

    :param svc_url: The URL pointing to the feature endpoint
    :type svc_url: str
    :param svc_data: A dictionary containing scraped data from an ESRI feature service endpoint
    :type svc_data: dict
    :returns: bool -- True if the layer is considered 'small'
    """
# FIXME needs refactoring, better error handling and better logic
    try:
        if svc_data['geometryType'] in ('esriGeometryPoint', 'esriGeometryMultipoint', 'esriGeometryEnvelope'):
            count_query = '/query?where=1%3D1&returnCountOnly=true&f=pjson'
            id_query = '/query?where=1%3D1&returnIdsOnly=true&f=json'
            r = requests.get(get_base_url(svc_url) + count_query, proxies=flask.g.proxies)
            if 'count' in r.json():
                return r.json()['count'] <= 2000
            r = requests.get(get_base_url(svc_url) + id_query, proxies=flask.g.proxies)
            if 'objectIds' in r.json():
                return len(r.json()['objectIds']) <= 2000
    except Exception:
        pass
    return False


def make_v1_feature_node(json_request, v2_node):
    """
    Generate a RAMP layer entry for an ESRI feature service.

    :param data: The initial payload to RCS (should contain a 'service_url' entry)
    :type data: dict
    :param id: An identifier for the layer (as this is unique it is generally supplied from :module:rcs )
    :type id: str
    :returns: dict -- a RAMP configuration fragment representing the ESRI layer
    """
    steal_fields = ['id', 'url', 'metadataUrl', 'catalogueUrl']
    node = {field: v2_node[field] for field in steal_fields if field in v2_node}
    r = requests.get(v2_node['url'] + '?f=json', proxies=flask.g.proxies)
    svc_data = r.json()
    node['displayName'] = json_request.get('service_name', None)
    node['nameField'] = json_request.get('display_field', None)
    if node.get('displayName', None) is None:
        node['displayName'] = svc_data['name']
    if node.get('nameField', None) is None:
        node['nameField'] = svc_data['displayField']

    node['minScale'] = svc_data.get('minScale', 0)
    node['maxScale'] = svc_data.get('maxScale', 0)
    node['datagrid'] = make_data_grid(svc_data)
    node['layerExtent'] = make_extent(svc_data)
    # NOTE: the fellowing line was commented out to supress the error when registering v1 nodes because feautre
    # layers do not have legend?f=json.  See functions make_symbology and get_legend_mapping for more details.
    # node['symbology'] = make_symbology(svc_data, v2_node['url'])
    node['aliasMap'] = make_alias_mapping(svc_data['fields'])
    if 'max_allowable_offset' in json_request:
        node['maxAllowableOffset'] = json_request['max_allowable_offset']
    if 'loading_mode' in json_request:
        node['mode'] = json_request['loading_mode']
    elif test_small_layer(node['url'], svc_data):
        node['mode'] = 'snapshot'
    node['geometryType'] = svc_data['geometryType']
    return node


def make_feature_node(req):
    """
    Parse ESRI feature specific content from a given request
    """
    result = {}
    if 'tolerance' in req:
        result['tolerance'] = req['tolerance']
    return result


def make_server_node(req):
    """
    Parse ESRI MapServer / FeatureServer specific content from a given request
    """
    result = {}
    if 'scrape_only' in req:
        result['layerEntries'] = [{'index': index} for index in req['scrape_only']]
    elif 'recursive' in req:
        query_service = requests.get(req['service_url'] + "?f=pjson", proxies=flask.g.proxies)
        service_json = query_service.json()
        result['service_url'] = req['service_url'].rstrip('1234567890')
        result['url'] = req['service_url'].rstrip('1234567890')
        sublayer_json = []
        if 'type' not in service_json:
            sublayer_json = [x for x in service_json['layers'] if x['parentLayerId'] == -1]
        else:
            sublayer_json = service_json['subLayers']
        result['layerEntries'] = [{'index': sl['id']} for sl in sublayer_json]
    else:
        result['layerEntries'] = []
    return result
