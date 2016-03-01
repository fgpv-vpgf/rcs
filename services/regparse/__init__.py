import wms, esri_feature, sigcheck
__all__ = ['esri_feature', 'sigcheck', 'wms', 'make_id', 'make_record']


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


def make_record(key, request, config):
    """
    Determine the data type to generate the appropriate record entry.
    """
    data = dict(key=key, request=request)
    if request['payload_type'] == 'wms':
        data['en'] = wms.make_node(request['en'], make_id(key, 'en'), config)
        data['fr'] = wms.make_node(request['fr'], make_id(key, 'fr'), config)
    else:
        data['en'] = esri_feature.make_node(request['en'], make_id(key, 'en'), config)
        data['fr'] = esri_feature.make_node(request['fr'], make_id(key, 'fr'), config)
    return data
