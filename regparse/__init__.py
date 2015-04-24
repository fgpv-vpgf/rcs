import wms, esri_feature, sigcheck
__all__ = ['esri_feature','wms','make_id','refresh_records','make_record']

def make_id( key, lang ):
    """
    Generates an RCS ID in the form rcs.a82d987e.en

    :param key: The key to use for generating the unique id (keys are shared amongst different languages)
    :type key: str
    :param lang: The two letter language code for generating the unique id
    :type lang: str
    :returns: str -- an id that should be unique amongst all RCS ids
    """
    return "{0}.{1}.{2}".format('rcs',key,lang)

# TODO think about the best place for this function
def refresh_records( day_limit, config ):
    import db, datetime, string
    valid = []
    invalid = {}
    query = ""
    if day_limit is None:
        query = "function(doc) { emit(doc._id, { updated: doc.updated_at, key: doc.data.key, request: doc.data.request }); }"
    else:
        min_age = datetime.date.today() - datetime.timedelta( days=day_limit )
        query = "function(doc) { if (doc.updated_at <= '$date') emit(doc._id, { updated: doc.updated_at, key: doc.data.key, request: doc.data.request }); }"
        query = string.Template(query).substitute( date=min_age )
    results = db.query( query )
    for r in results:
        key = r['id']
        print r
        if 'request' not in r['value']:
            invalid[key] = 'previous request was not cached (request caching added in 1.8.0)'
            continue
        req = r['value']['request']
        try:
            data = make_record( key, req, config )
            db.put_doc( key, { 'type':req['payload_type'], 'data':data } )
            valid.append( key )
        except Exception as e:
            invalid[key] = str(e)
            
    return { "updated":valid, "errors":invalid }

def make_record( key, request, config ):
    data = dict( key=key, request=request )
    if request['payload_type'] == 'wms':
        data['en'] = wms.make_node( request['en'], make_id(key,'en'), config )
        data['fr'] = wms.make_node( request['fr'], make_id(key,'fr'), config )
    else:
        data['en'] = esri_feature.make_node( request['en'], make_id(key,'en'), config )
        data['fr'] = esri_feature.make_node( request['fr'], make_id(key,'fr'), config )
    return data
