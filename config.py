STORAGE_DB='rcs_cache'
AUTH_DB='rcs_auth'
DB_CONN='http://localhost:5984/'

SIG_CHECK=True
METADATA_URL='http://www2.dmsolutions.ca/cgi-bin/mswfs_gmap?version=1.3.0&request=getcapabilities&service={0}'
CATALOGUE_URL='http://www2.dmsolutions.ca/cgi-bin/mswfs_gmap?version=1.3.0&request=getcapabilities&service={0}'

LOG_FILE='rcs.log'
ACCESS_LOG='access.log'
LOG_ROTATE_BYTES=200000
LOG_BACKUPS=10
# https://docs.python.org/2/library/logging.html#levels
# common options DEBUG 10; ERROR 40
LOG_LEVEL=10

REG_SCHEMA='schemas/rcs_reg_schema_v1_2_0.json'

URL_PREFIX=''
