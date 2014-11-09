# Deployment

RCS uses Python and MongoDB and should be deployable on any platform that
supports both.  Currently deployment notes are provided only for Windows (and
tested with 2008r2 and 2012).

## Windows via IIS and FastCGI

### Install [MongoDB](http://www.mongodb.org)
1. Run the installer (64bit version tested)
2. Create a directory for data and logs (e.g. `c:\mongo\data\` and `c:\mongo\logs\`)
3. Create a configuration file for the DB (e.g. `c:\mongo\mongod.cfg`)
```yaml
systemLog:
  destination: file
  path: "c:\\mongo\\logs\\mongodb.log"
  quiet: true
  logAppend: true
storage:
  dbPath: "c:\\mongo\\data"
  directoryPerDB: true
```
4. Install MongoDB as a service:
   `"c:\Program Files\MongoDB 2.6 Standard\bin\mongod.exe" --config "c:\mongo\mongod.cfg" --install`
5. Start MongoDB: `net start MongoDB`
6. Create an admin user and an rcs user (run `mongo.exe` for a shell)
```js
use admin
db.createUser({user:"admin",pwd:"changeme",roles:["root"]})
use rcs
db.createUser({user:"rcs",pwd:"changeme",roles:[{role:"readWrite"}]})
```
7. Enable authentication in the config by adding the following:
```yaml
security:
  authorization: enabled
```
8. Restart the MongoDB service `net stop mongodb`, `net start mongodb`

### Configure Python Environment

1. Ensure python is a 2.7.x release
1. Install pip (https://pip.pypa.io/en/latest/installing.html)
1. Install virtualenv `pip install virtualenv`
1. Create python virtual environment `virtualenv c:\inetpub\rcs`
1. Activate the virtualenv `scripts\activate`
1. Extract the deployment package (or for dev environments clone this repo)
1. Install the project dependencies `pip install -r requirements.txt`
1. Test the installation `python rcs.py`

### IIS Integration

1. Ensure IIS has CGI support
1. Create a website in IIS and point it to the Python virtual environment
1. Go to the website | Handler Mappings | Add Module Mapping ...
```

```
