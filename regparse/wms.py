import requests

def make_feature_info( data ):
    fi_type = data.get('feature_info_type',None) 
    if fi_type == 'text/plain':
        return { 'mimeType':fi_type, 'parser':'stringParse' }
    if fi_type == 'text/html':
        return { 'mimeType':fi_type, 'parser':'htmlRawParse' }
    if fi_type == 'application/json':
        return { 'mimeType':fi_type, 'parser':'jsonRawParse' }
    return None

def make_node( data, id ):
    wms_node = { 'id': id }
    wms_node['url'] = data['service_url']
    wms_node['layerName'] = data['layer']
    wms_node['displayName'] = data['layer']
    wms_node['format'] = 'image/png'
    if 'legend_format' in data:
        wms_node['legendMimeType'] = data['legend_format']
    fi_node = make_feature_info( data )
    if fi_node is not None:
        wms_node['featureInfo'] = fi_node
    return wms_node
