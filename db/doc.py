"""
Methods for dealing with DB document requests
"""
import pycouchdb, datetime, string

_db = None

def init_doc_db( url, db_name ):
    global _db
    client = pycouchdb.Server( url )
    _db = client.database( db_name )

def remap( key_map, fragment ):
    f = {}
    for k,v in fragment.iteritems():
        if k in key_map:
            f[key_map[k]] = v
        else:
            f[k] = v
    return f

def gc_09( col ):
    return remap( { 'orderable':'isSortable', 'type':'sortType' }, col )

def gc_10( col ):
    return remap( { 'isSortable':'orderable', 'sortType':'type' }, col )

def version_conversion( ver, fragment ):
    """
    Convert a JSON fragment to the target version
    """

    if ver == '0.9':
        if 'datagrid' not in fragment:
            return fragment
        fragment['datagrid']['gridColumns'] = [ gc_09(x) for x in fragment['datagrid']['gridColumns'] ]
        return fragment
    elif ver == '1':
        if 'datagrid' not in fragment:
            return fragment
        fragment['datagrid']['gridColumns'] = [ gc_10(x) for x in fragment['datagrid']['gridColumns'] ]
        return fragment
    raise Exception("Invalid version")

def get_doc( key, lang, ver ):
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
    except pycouchdb.exceptions.NotFound as nfe:
        return None
    if o is not None:
        fragment = o.get('data',{}).get(lang,None)
        if fragment is not None:
            fragment = version_conversion( ver, fragment )
            result = { 'layers': {} }
            result['layers'][ o['type'] ] = [ fragment ]
            if 'geometryType' in result['layers'][ o['type'] ][0]:
                del result['layers'][ o['type'] ][0]['geometryType']
            return result
    return None

def get_raw( key ):
    """
    Fetch a record from the document store, no nonsense.

    :param key: The key to search the document store for
    :type key: str
    :returns: dict -- A dictionary representing the value in the database; None -- key not found
    """
    try:
        o = _db.get(key)
    except pycouchdb.exceptions.NotFound as nfe:
        return None
    return o

def put_doc( key, doc ):
    try:
        _db.delete( key )
    except pycouchdb.exceptions.NotFound as nfe:
        pass
    doc['_id'] = key
    doc['updated_at'] = datetime.date.today().isoformat()
    _db.save( doc )

def query( q ):
    return _db.temporary_query( q )

def delete_doc( key ):
    _db.delete( key )
