"""
A WMS "parser" (barely does any parsing at the moment).
"""
import requests, metadata

def make_feature_info( data ):
    """
    Make a RAMP feature info node, identifying the correct default parser to be
    used based on the MIME type of the feature info request.

    Currently accepted MIME types (in order of preference):
        'text/html'
        'text/plain'
        'application/json'

    :param data: The initial payload to RCS
    :type data: dict
    :returns: dict -- A feature info configuration fragment; None if no valid mimeType was set
    """
    fi_type = data.get('feature_info_type',None) 
    if fi_type == 'text/html':
        return { 'mimeType':fi_type, 'parser':'htmlRawParse' }
    if fi_type == 'text/plain':
        return { 'mimeType':fi_type, 'parser':'stringParse' }
    if fi_type == 'application/json':
        return { 'mimeType':fi_type, 'parser':'jsonRawParse' }
    return None

def make_node( data, id, config=None ):
    """
    Generate a RAMP layer entry for a WMS.

    :param data: The initial payload to RCS
    :type data: dict
    :param id: An identifier for the layer (as this is unique it is generally supplied from :module:rcs )
    :type id: str
    :returns: dict -- a RAMP configuration fragment representing the WMS layer
    """
    wms_node = { 'id': id }
    wms_node['url'] = data['service_url']
    wms_node['layerName'] = data['layer']
    wms_node['displayName'] = data['layer']
    if 'service_name' in data:
        wms_node['displayName'] = data['service_name']
    wms_node['format'] = 'image/png'
    metadata_url, catalogue_url = metadata.get_url( data, config )
    if metadata_url:
        wms_node['metadataUrl'] = metadata_url
        wms_node['catalogueUrl'] = catalogue_url
    if 'legend_format' in data:
        wms_node['legendMimeType'] = data['legend_format']
    fi_node = make_feature_info( data )
    if fi_node is not None:
        wms_node['featureInfo'] = fi_node
    return wms_node
