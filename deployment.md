# Deployment

RCS uses Python and MongoDB and should be deployable on any platform that
supports both.  Currently deployment notes are provided only for Windows (and
tested with 2008r2 and 2012).

## Windows via IIS and FastCGI

Install [MongoDB](http://www.mongodb.org)
1. Run the installer (64bit version tested)
2. Create a directory for data and logs (e.g. `c:\mongo\data\` and `c:\mongo\logs\`)
3. Create a configuration file for the DB (e.g. `c:\mongo\mongod.cfg`)
```
systemLog:
  destination: file
  path: "c:\\mongo\\logs\\mongodb.log"
  quiet: true
  logAppend: true
storage:
  dbPath: "c:\\mongo\\db"
  directoryPerDB: true
```
