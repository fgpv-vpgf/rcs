import config, pycouchdb
client = pycouchdb.Server( config.DB_CONN )
auth_db = client.database( config.AUTH_DB )

auth_db.save( { '_id':'jstest', 'key':'test_-k' } )
auth_db.save( { '_id':'1', 'key':'n4bQgYhMfWWaL-qgxVrQFaO_TxsrC4Is0V1sFbDwCgg' } )
