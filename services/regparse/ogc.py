import requests
import xml.etree.ElementTree as ETree

"""
A WMS "parser" (barely does any parsing at the moment).
"""

# TODO test me


def make_feature_info(fi_type):
    """
    Make a RAMP feature info node, identifying the correct default parser to be
    used based on the MIME type of the feature info request.

    Currently accepted MIME types (in order of preference):
        'text/html'
        'text/plain'
        'application/json'

    :param fi_type: The feature info MIME type
    :type data: str
    :returns: dict -- A feature info configuration fragment; None if no valid mimeType was set
    """
    if fi_type in ['text/html', 'text/html;fgpv=summary']:
        return {'mimeType': fi_type, 'parser': 'htmlRawParse'}
    if fi_type == 'text/plain':
        return {'mimeType': fi_type, 'parser': 'stringParse'}
    if fi_type == 'application/json':
        return {'mimeType': fi_type, 'parser': 'jsonRawParse'}
    return None


def make_v1_wms_node(req, v2_node, config=None):
    """
    Generate a RAMP layer entry for a WMS.

    :param data: The initial payload to RCS
    :type data: dict
    :param id: An identifier for the layer (as this is unique it is generally supplied from :module:rcs )
    :type id: str
    :returns: dict -- a RAMP configuration fragment representing the WMS layer
    """
    if len(v2_node['layerEntries']) != 1:
        # need to have a single entry for v1 records (which were one layer per registration node)
        return None

    steal_fields = ['id', 'url', 'metadataUrl', 'catalogueUrl', 'legendMimeType']
    wms_node = {field: v2_node[field] for field in steal_fields if field in v2_node}
    wms_node['layerName'] = v2_node['layerEntries'][0]['id']
    wms_node['displayName'] = v2_node.get('name', wms_node['layerName'])
    wms_node['format'] = 'image/png'
    fi_node = make_feature_info(req.get('feature_info_format', None))
    if fi_node is not None:
        wms_node['featureInfo'] = fi_node
    return wms_node


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def parseCapabilities(capabilties_xml_string):
    """
    Parses a Capabilities document for fields we need for registration.

    :param capabilties_xml_string: The URL to the service's Capabilities document
    :type capabilties_xml_string: str
    :returns: dict -- the Name, Title, and Queryable values of all layers in the service.
    """
    ret = {}
    xmldoc = ETree.fromstring(capabilties_xml_string)
    namespace = xmldoc.tag[0:(xmldoc.tag.index('}') + 1)]
    for layer in xmldoc.iter(namespace + 'Layer'):
        id = layer.find(namespace + 'Name')
        if id != None:
            id = id.text
            title = layer.find(namespace + 'Title').text
            queryable = (layer.attrib)['queryable']
            ret[id] = dict(id=id, title=title, queryable=queryable)
    return ret


def make_wms_node(req):
    """
    Parse WMS specific content from a given request
    """
    result = {}
    endpoint = req['service_url']
    if '?' in endpoint:
        # the provided service url contains a query string
        endpoint += '&SERVICE=WMS&REQUEST=GetCapabilities'
    else:
        endpoint += '?SERVICE=WMS&REQUEST=GetCapabilities'
    query_service = requests.get(endpoint).content
    layer_params = parseCapabilities(query_service)
    if 'feature_info_format' in req:
        result['featureInfoMimeType'] = req['feature_info_format']
    legend_format = req.get('legend_format', None)
    if legend_format in ['image/png', 'image/gif', 'image/jpeg', 'image/svg', 'image/svg+xml']:
        result['legendMimeType'] = legend_format
    if 'scrape_only' in req:
        result['layerEntries'] = [{'id': id, 'queryable': layer_params[id]['queryable']}
                                  for id in req['scrape_only']]
    elif 'recursive' in req:
        result['layerEntries'] = [{
                                  'id': layer_params[i]['id'],
                                  'name': layer_params[i]['title'],
                                  'queryable': layer_params[i]['queryable']} for i in layer_params]
    else:
        result['layerEntries'] = []
    return result
