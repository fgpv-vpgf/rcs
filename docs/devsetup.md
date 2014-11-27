# Development Setup

For development we will be using the built in Flask server, no separate web server
required.  CouchDB will also be installed in admin party (every connection has admin
rights) mode.

### Install [CouchDB](http://couchdb.apache.org/)
1. Run the installer
1. Open a web browser and navigate to http://127.0.0.1:5984/_utils
1. Create a database `rcs_cache` (navigate to Overview | Create Database)
1. Create a second database `rcs_sync`

## Configure Python Environment

1. Ensure python is a 2.7.x release
1. Install pip (https://pip.pypa.io/en/latest/installing.html)
1. Install virtualenv `pip install virtualenv`
1. Create python virtual environment `virtualenv c:\projects\rcs`
1. Activate the virtualenv `scripts\activate`
1. Clone the repo, if you like having the repo in the same top level as the virtualenv do the following
    ```
    cd c:\projects\rcs
    git init
    git remote add origin git@github.com:RAMP-PCAR/RCS.git
    git fetch
    ```
1. Install the project dependencies `pip install -r requirements.txt`
1. Make any path changes necessary to `config.py` (if you followed the above there should be none)
1. Test the installation `python rcs.py` (this will run a test server on localhost)
