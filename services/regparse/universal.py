import metadata, requests, wms, esri_feature


remapped_types = {'esriMapServer': 'esriDynamic', 'esriFeatureServer': 'esriDynamic'}


class ServiceTypes:
    WMS = 'ogcWms'
    WMTS = 'ogcWmts'
    MAP_SERVER = 'esriMapServer'
    FEATURE_SERVER = 'esriFeatureServer'
    FEATURE = 'esriFeature'
    TILE = 'esriTile'
    IMAGE = 'esriImage'


parser_map = {
    ServiceTypes.WMS: wms.make_node,
    ServiceTypes.FEATURE: esri_feature.make_node,
}


class ServiceEndpointException(Exception):
    """
    An exception encoding all problems with metadata parsing and retrival.
    """
    def __init__(self, msg, inner_exception=None):
        self.message = msg
        self.inner_exception = inner_exception

    def __str__(self):
        return 'ServiceEndpointException {0}'.format(self.message)


def get_endpoint_type(endpoint):
    """
    Determine the type of the endpoint
    """
    try:
        r = requests.get(endpoint)
        ct = r.headers['content-type']
        if (ct == 'text/xml'):
            # XML response means WMS or WMTS (latter is not implemented)
            # FIXME type detection should be much more robust, add proper XML parsing, ...
            return ServiceTypes.WMS
        else:
            r = requests.get(endpoint+'?f=json')
            data = r.json()
            if 'type' in data:
                if data['type'] == 'Feature Layer':
                    return ServiceTypes.FEATURE
                elif data['type'] == 'Raster Layer':
                    return ServiceTypes.MAP_SERVER
                elif data['type'] == 'Group Layer':
                    return ServiceTypes.MAP_SERVER
            elif 'singleFusedMapCache' in data:
                if data['singleFusedMapCache']:
                    return ServiceTypes.TILE
                else:
                    return ServiceTypes.MAP_SERVER
            elif 'allowGeometryUpdates' in data:
                return ServiceTypes.FEATURE_SERVER
            elif 'allowedMosaicMethods' in data:
                return ServiceTypes.IMAGE
    except Exception as e:
        raise ServiceEndpointException('Problem communicating with service endpoint {0}'.format(e.message), e)
    raise ServiceEndpointException('Endpoint({0}) did not match any known service type'.format(endpoint))


def make_id(key, lang):
    """
    Generates an RCS ID in the form rcs.a82d987e.en

    :param key: The key to use for generating the unique id (keys are shared amongst different languages)
    :type key: str
    :param lang: The two letter language code for generating the unique id
    :type lang: str
    :returns: str -- an id that should be unique amongst all RCS ids
    """
    return "{0}.{1}.{2}".format('rcs', key, lang)


def make_node(key, json_request, config):
    """
    Construct a basic layer node which could be consumed by the viewer.
    """
    langs = config['LANGS']
    node = {lang: {} for lang in langs}
    svc_types = {lang: get_endpoint_type(json_request[lang]['service_url']) for lang in langs}
    if len(set(svc_types.values())) > 1:
        raise ServiceEndpointException('Mismatched service types across languages {0}'.format(svc_types.values()))
    for lang in langs:
        n = node[lang]
        n['id'] = make_id(key, lang)
        ltype = remapped_types.get(svc_types[lang], svc_types[lang])
        n['layerType'] = ltype
        if 'service_type' in json_request[lang] and json_request[lang]['service_type'] != svc_types[lang]:
            msg = 'Mismatched service type in {0} object, endpoint identified as {1} but provided as {2}' \
                  .format(lang, svc_types[lang], json_request[lang]['service_type'])
            raise ServiceEndpointException(msg)
        n['url'] = json_request[lang]['service_url']
        m_url, c_url = metadata.get_url(json_request[lang], config)
        if c_url:
            node[lang]['metadataUrl'] = m_url
            node[lang]['catalogueUrl'] = c_url
        n.update(parser_map[ltype](json_request))
        if 'service_name' in json_request[lang]:
            # important to do this last so it overwrites anything scraped from the custom parser
            n['name'] = json_request[lang]['service_name']
    return node
