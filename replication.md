# Replication

RCS was designed to be deployed in a load balanced environment.  The following
steps can be used to setup CouchDB for master-master replication if it is deployed
on systems which follow the same partitioning as the load balancer.

The notes are relatively straightforward, but only cover simple network architectures
where a few servers are connected over strong links.

## Replication Setup

For the following instructions take a sample setup of servers labeled 'server1 ... server4'
in a 4 node load balanced setup.

Perform the following for each server
1. Load the admin interface (http://127.0.0.1/_utils)
1. Add the following documents to the database `_replicator`
```js
{
    "source": "http://user:pass@serverX:5984/rcs_cache",
    "target": "rcs",
    "continuous": true
}
```
