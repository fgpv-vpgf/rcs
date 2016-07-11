import metadata, requests, ogc, esri, re, flask


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
    ServiceTypes.WMS: ogc.make_wms_node,
    ServiceTypes.WMTS: ogc.make_wms_node,
    ServiceTypes.MAP_SERVER: esri.make_server_node,
    ServiceTypes.FEATURE_SERVER: esri.make_server_node,
    ServiceTypes.FEATURE: esri.make_feature_node,
    ServiceTypes.TILE: lambda *args: {},
    ServiceTypes.IMAGE: lambda *args: {},
}

esri_types = [ServiceTypes.MAP_SERVER, ServiceTypes.FEATURE_SERVER, ServiceTypes.FEATURE, ServiceTypes.TILE,
              ServiceTypes.IMAGE]


class ServiceEndpointException(Exception):
    """
    An exception encoding all problems with metadata parsing and retrival.
    """
    def __init__(self, msg, inner_exception=None):
        self.message = msg
        self.inner_exception = inner_exception

    def __str__(self):
        return 'ServiceEndpointException {0}'.format(self.message)


def get_endpoint_type(endpoint, type_hint=None):
    """
    Determine the type of the endpoint
    """
    try:
        esri_regex = re.compile('/(mapserver|featureserver)/?\d*$', re.IGNORECASE)
        xml_regex = re.compile('(text|application)/.*xml', re.IGNORECASE)
        is_esri = esri_regex.search(endpoint) or type_hint in esri_types
        if '?' not in endpoint and not is_esri:
            # probably isn't an ESRI endpoint so try GetCapabilities
            endpoint += '?VERSION=1.1.1&REQUEST=GetCapabilities&SERVICE=wms'
        r = requests.get(endpoint)
        print r.status_code
        print r.headers
        ct = r.headers['content-type']
        if (xml_regex.search(ct)):
            # XML response means WMS or WMTS (latter is not implemented)
            # FIXME type detection should be much more robust, add proper XML parsing, ...
            return ServiceTypes.WMS
        elif is_esri:
            r = requests.get(endpoint+'?f=json', proxies=flask.g.proxies)
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
        raise ServiceEndpointException('Problem communicating with service endpoint {0} {1}'
                                       .format(endpoint, e.message), e)
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
    v1 = None
    svc_types = {lang: get_endpoint_type(json_request[lang]['service_url'], json_request[lang].get('service_type'))
                 for lang in langs}
    if len(set(svc_types.values())) > 1:
        raise ServiceEndpointException('Mismatched service types across languages {0}'.format(svc_types.values()))
    if svc_types.values()[0] in [ServiceTypes.WMS, ServiceTypes.FEATURE]:
        v1 = {lang: {} for lang in langs}
    for lang in langs:
        n = node[lang]
        n['id'] = make_id(key, lang)
        ltype = svc_types[lang]
        n['layerType'] = remapped_types.get(ltype, ltype)
        if 'service_type' in json_request[lang] and json_request[lang]['service_type'] != svc_types[lang]:
            msg = 'Mismatched service type in {0} object, endpoint identified as {1} but provided as {2}' \
                  .format(lang, svc_types[lang], json_request[lang]['service_type'])
            raise ServiceEndpointException(msg)
        n['url'] = json_request[lang]['service_url']
        m_url, c_url = metadata.get_url(json_request[lang], config)
        if c_url:
            node[lang]['metadataUrl'] = m_url
            node[lang]['catalogueUrl'] = c_url
        if 'display_field' in json_request[lang]:
            n['nameField'] = json_request[lang]['display_field']
        n.update(parser_map[ltype](json_request[lang]))
        if 'service_name' in json_request[lang]:
            # important to do this last so it overwrites anything scraped from the custom parser
            n['name'] = json_request[lang]['service_name']
        if ltype == ServiceTypes.WMS:
            v1[lang] = ogc.make_v1_wms_node(json_request[lang], n)
        elif ltype == ServiceTypes.FEATURE:
            v1[lang] = esri.make_v1_feature_node(json_request[lang], n)
    return node, v1
