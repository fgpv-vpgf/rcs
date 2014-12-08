import pycouchdb

_db = None

def init_db( url, db_name ):
    global _db
    client = pycouchdb.Server( url )
    _db = client.database( db_name )

def get_key( sender_id ):
    """
    Fetch the correct key for the client

    :param sender_id: The sender's identifier
    :type sender_id: str
    :returns: str -- the pre-shared key for the sender
    """
    global _db
    return _db.get( sender_id )['key']
