.. _config:

RCS Configuration Options
========================

LOG_FILE
    Name of the log file
LOG_LEVEL
    Follows `Python log levels <https://docs.python.org/3/library/logging.html#logging-levels>`_
LOG_BACKUPS
    Number of backups (rotated log files) to keep
LOG_ROTATE_BYTES
    Size in bytes at which logs should be rotated
ACCESS_LOG
    Name of the access log file, if not present access requests will not be logged
URL_PREFIX
    A general prefix for the application, useful if you want to have side by side installs
    of RCS.  It should include an opening / (e.g. ``/rcs_ecdmp``).
STORAGE_DB
    The name of the couchdb database for storing the cached requests
AUTH_DB
    Name of the database holding the API signing keys
DB_CONN
    A database connection string (typically an http url, ex: ``http://localhost:5984/``)
SIG_CHECK
    Boolean value indicating if signature verification should be done on requests
METADATA_URL
    Template URL for metadata, should include a ``{0}`` parameter for string replacement
CATALOGUE_URL
    Template URL for the catalogue page, should include a ``{0}`` parameter for string replacement
REG_SCHEMA
    Path to the JSON schema to be used for validating PUT requests
LANGS
    Must match the languages required by the schema (e.g. 'en', 'fr')
HTTP_PROXY
    A proxy URL to be used when registering layers.  Should be in the form of ``http://[server]:[port]``.
PROD
    Adds checks for production systems to ensure test keys like ``jstest`` and ``ecdmpdev`` are not used, and ensures that DEBUG_ENDPOINTS and SIG_CHECK are set to false and true, respectively.
DEBUG_ENDPOINTS
    Enables the /accesslog, /logs, and /all_keys endpoints, should be turned off in Production environments.
