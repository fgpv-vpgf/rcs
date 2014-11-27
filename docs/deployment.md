# Deployment

RCS uses Python and CouchDB and should be deployable on any platform that
supports both.  Currently deployment notes are provided only for Windows (and
tested with 2008r2 and 2012).

## Windows via IIS and FastCGI

### Install [CouchDB](http://couchdb.apache.org/)
1. Run the installer
1. Open a web browser and navigate to http://127.0.0.1:5984/_utils
1. Setup the admin account (see link in bottom left of the window)
1. Update the configuration to listen on the correct network address (Tools | Configuration | bind_addr)
1. Create a database `rcs_cache` (navigate to Overview | Create Database)
1. Update the security for the `rcs_cache` database set Admin Roles: `["rcs"]` and Member Roles: `["rcs"]`
1. Create a second database `rcs_sync` with the same permissions
1. Add a new user to the `_users` database (Overview | _users | New Document)
1. Select source and enter the following then save document
```js
{
    "_id": "org.couchdb.user:rcs",
    "name": "rcs",
    "roles": ["rcs"],
    "type": "user",
    "password": "changeme"
}
```
1. Logout and attempt to login as user `rcs` to test the setup
1. Confirm that access to `_users` is restricted and access to `rcs_cache` and `rcs_sync` is enabled

### Configure Python Environment

1. Ensure python is a 2.7.x release
1. Get an RCS release package `rcs-X.Y.Z.zip`
1. Extract the release package, it should be somewhere IIS can be configured to read from `c:\inetpub\rcs-X.Y.Z`
1. [Optional] Get prepackaged dependencies (should be a directory full of `.whl` files)
1. Install pip (https://pip.pypa.io/en/latest/installing.html)
1. Install virtualenv `pip install virtualenv`
1. Create python virtual environment in the release location and activate it
```
cd c:\inetpub\rcs-X.Y.Z
virtualenv .
scripts\activate
```
1. Install the project dependencies:
    * via internet `pip install -r requirements.txt`
    * via local wheel cache `pip install --use-wheel --no-index --find-links=c:\path\to\wheel\dir -r requirements.txt`
1. Update the configuration in `config.py` or set the environment variable `RCS_CONFIG`
   to point to a config which overrides the defaults set in `config.py`
1. Update the configuration variable for `REG_SCHEMA` to an absolute path (e.g. `c:\\inetpub\\rcs-X.Y.Z`
   -- use double backslashes to avoid string escape codes)
1. Ensure the `DB_CONN` variable in the config matches the account, password and other settings
   from the CouchDB installation
1. Test the installation `python rcs.py` (this will run a test server on localhost)

### IIS Integration

1. Ensure IIS has CGI support (http://www.iis.net/configreference/system.webserver/cgi)
1. Create a website in IIS and point it to the Python virtual environment
1. Go to the website | Handler Mappings | Add Module Mapping ...
```yaml
Request Path: *
Module: FastCgiModule
Executable: C:\inetpub\rcs-X.Y.Z\Scripts\python.exe|C:\inetpub\rcs-X.Y.Z\wfastcgi.py
Name: (name)
```
1. Go back to the server settings | FastCgi Settings | Right click Edit
1. Select Environment variables and add the following:
```yaml
PYTHONPATH: C:\inetpub\rcs-X.Y.Z\
WSGI_HANDLER: rcs.app
```
