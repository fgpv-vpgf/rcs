STORAGE_DB = 'rcs_cache'
AUTH_DB = 'rcs_auth'
DB_CONN = 'http://localhost:5984/'

SIG_CHECK = False
METADATA_URL = 'http://www2.dmsolutions.ca/cgi-bin/mswfs_gmap?version=1.3.0&request=getcapabilities&service={0}'
CATALOGUE_URL = 'http://www2.dmsolutions.ca/cgi-bin/mswfs_gmap?version=1.3.0&request=getcapabilities&service={0}'

LOG_FILE = 'rcs.log'
ACCESS_LOG = 'access.log'
LOG_ROTATE_BYTES = 200000
LOG_BACKUPS = 10
# https://docs.python.org/2/library/logging.html#levels
# common options DEBUG 10; ERROR 40
LOG_LEVEL = 10

REG_SCHEMA = 'schemas/rcs_reg_schema_v2_0_0.json'
# LANGS must match the languages required by the schema
LANGS = ['en', 'fr']

URL_PREFIX = ''

DEBUG_ENDPOINTS = False

# FEATURE_SERVICE_PROXY='http://127.0.0.1:8001'
