"""
Methods for dealing with DB document requests
"""
import pycouchdb, datetime


_db = None


def init_doc_db(url, db_name):
    global _db
    client = pycouchdb.Server(url)
    _db = client.database(db_name)


def remap(key_map, fragment):
    f = {}
    for k, v in fragment.iteritems():
        if k in key_map:
            f[key_map[k]] = v
        else:
            f[k] = v
    return f


def gc_09(col):
    return remap({'orderable': 'isSortable', 'type': 'sortType'}, col)


def gc_10(col):
    return remap({'isSortable': 'orderable', 'sortType': 'type'}, col)


def version_conversion(ver, fragment):
    """
    Convert a JSON fragment to the target version
    """

    if ver == '0.9':
        if 'datagrid' not in fragment:
            return fragment
        fragment['datagrid']['gridColumns'] = [gc_09(x) for x in fragment['datagrid']['gridColumns']]
        return fragment
    elif ver == '1':
        if 'datagrid' not in fragment:
            return fragment
        fragment['datagrid']['gridColumns'] = [gc_10(x) for x in fragment['datagrid']['gridColumns']]
        return fragment
    raise Exception("Invalid version")


def get_doc(key, lang, ver):
    """
    Fetch a record from the document store and output a RAMP compatible configuration.

    :param key: The key to search the document store for
    :type key: str
    :param lang: A two letter language code identifying the language for the response
    :type lang: str
    :returns: dict -- A dictionary representing a JSON configuration fragment for RAMP; None -- key not found
    """
    try:
        o = _db.get(key)
    except pycouchdb.exceptions.NotFound:
        return None
    if o is not None:
        # FIXME very hacky setup for integration testing, clean this up
        if ver == '2':
            fragment = o.get('layer_config', {}).get(lang, None)
            if fragment is not None:
                result = dict(layers=[fragment])
                return result
            return None

        # attempt to get v1 style data from the v2 style DB format
        fragment = o.get('v1_config', {}).get(lang, None)
        if fragment is not None:
            map_types = {'ogcWms': 'wms', 'esriFeature': 'feature'}
            fragment = version_conversion(ver, fragment)
            result = {'layers': {}}
            svc_type = map_types.get(o['service_type'], None)
            if svc_type is None:
                return None
            result['layers'][svc_type] = [fragment]
            if 'geometryType' in result['layers'][svc_type][0]:
                del result['layers'][svc_type][0]['geometryType']
            return result

        # attempt to get the v1 style data from a record that is still in the old DB format
        # this should be deprecated when v3 comes along
        fragment = o.get('data', {}).get(lang, None)
        if fragment is not None:
            fragment = version_conversion(ver, fragment)
            result = {'layers': {}}
            result['layers'][o['type']] = [fragment]
            if 'geometryType' in result['layers'][o['type']][0]:
                del result['layers'][o['type']][0]['geometryType']
            return result
    return None


def get_raw(key):
    """
    Fetch a record from the document store, no nonsense.

    :param key: The key to search the document store for
    :type key: str
    :returns: dict -- A dictionary representing the value in the database; None -- key not found
    """
    try:
        o = _db.get(key)
    except pycouchdb.exceptions.NotFound:
        return None
    return o


def get_all(lang):
    """
    Display all keys and their service URLs.
    """
    try:
        allkeys = [{'key': key} for key in _db.all(None, None, 'True')]
        ids_and_urls = []
        for i in allkeys:
            for key, elem in i.items():
                ids_and_urls.append({elem['_id']: elem['request'][lang]['service_url']})
        return ids_and_urls
    except pycouchdb.exceptions.NotFound:
        pass
    return None


def put_doc(key, svc_type, req, **kw):
    doc = {}
    for k, v in kw.items():
        if v is not None:
            doc[k] = v
    try:
        _db.delete(key)
    except pycouchdb.exceptions.NotFound:
        doc['created_at'] = datetime.date.today().isoformat()
    doc['_id'] = key
    doc['request'] = req
    doc['version'] = '2.0'
    doc['service_type'] = svc_type
    doc['updated_at'] = datetime.date.today().isoformat()
    _db.save(doc)


def query(q):
    return _db.temporary_query(q)


def delete_doc(key):
    _db.delete(key)
