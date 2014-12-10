"""
A module to parse metadata URLs.  Common logic to other parsers.
"""
import requests

class MetadataException(Exception):
    """
    An exception encoding all problems with metadata parsing and retrival.
    """
    def __init__(self, msg, inner_exception):
        self.message = msg
        self.inner_exception = inner_exception

def get_url( data, config ):
    """
    Returns a metadata URL based on the input object.

    Performs the following tests:
	1. If metadata.url is present it takes precedence
	2. If metadata.uuid is present config['METADATA_URL'] + uuid  is used
    3. The metadata URL is tested, if it does not return a status 200 with
       content-type 'text/xml' or 'application/xml' and non zero length content
        then a MetadataException is raised

    :param data: JSON payload from the registration request
    :param config: the configuration object for the application (used for looking up METADATA_URL)
    :returns: str -- a URL with the metadata to be retrieved; None if metadata
        is not present in the original request
    """
    url = None
    if 'metadata' not in data:
        return url
    if 'url' in data['metadata']:
        url = data['metadata']['url']
    elif 'uuid' in data['metadata']:
        if 'METADATA_URL' not in config:
            raise MetadataException('Config object missing METADATA_URL property')
        url = config['METADATA_URL'] + data['metadata']['uuid']
    else:
        raise MetadataException('Metadata object was not structured as expected')

    try:
        r = requests.get( url )
    except Exception as e:
        raise MetadataException('Exception during metadata URL request {0}'.format(e.message), e)

    if r.headers.get('content-type') not in ('application/xml','text/xml'):
        raise MetadataException( 'Expected xml MIME type, got {0}'.format( r.headers.get('content-type') ) )
    if not len(r.content):
        raise MetadataException( 'Got a zero length request' )
    if r.status_code != requests.codes.ok:
        raise MetadataException( 'Bad HTTP status code received {0}'.format( r.status_code ) )

    return url
