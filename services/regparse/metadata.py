"""
A module to parse metadata URLs.  Common logic to other parsers.
"""
import requests


class MetadataException(Exception):
    """
    An exception encoding all problems with metadata parsing and retrival.
    """
    def __init__(self, msg, inner_exception=None):
        self.message = msg
        self.inner_exception = inner_exception

    def __str__(self):
        return 'MetadataException {0}'.format(self.message)


def test_url(url, response_types, msg_prefix):
    try:
        r = requests.get(url)
    except Exception as e:
        raise MetadataException('{0} "{1}" request failed with error "{2}"'.format(msg_prefix, url, e.message), e)

    if r.headers.get('content-type').split(';')[0] not in response_types:
        raise MetadataException('{0} "{1}" could not be retrieved: expected "{2}", got "{3}"'
                                .format(msg_prefix, url, str(response_types), r.headers.get('content-type')))
    if not len(r.content):
        raise MetadataException('{0} "{1}" could not be retrieved: Got a zero length request'
                                .format(msg_prefix, url))
    if r.status_code != requests.codes.ok:
        raise MetadataException('{0} "{1}" could not be retrieved: bad HTTP status code received {2}'
                                .format(msg_prefix, url, r.status_code))


def get_url(data, config):
    """
    Returns a metadata URL based on the input object.

    Performs the following tests:
    1. If metadata.metadata_url is present it takes precedence
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
    catalogue_url = None
    if 'metadata' not in data:
        return url, catalogue_url
    if 'metadata_url' in data['metadata']:
        url = data['metadata']['metadata_url']
        catalogue_url = data['metadata']['catalogue_url']
    elif 'uuid' in data['metadata']:
        for x in ['METADATA_URL', 'CATALOGUE_URL']:
            if x not in config:
                raise MetadataException('Config object missing {0} property'.format(x))
        url = config['METADATA_URL'].format(data['metadata']['uuid'])
        catalogue_url = config['CATALOGUE_URL'].format(data['metadata']['uuid'])
    else:
        raise MetadataException('Metadata object was not structured as expected')

    test_url(url, ['application/xml', 'text/xml'], 'Metadata URL:')
    test_url(catalogue_url, ['text/html'], 'Catalogue URL:')

    return url, catalogue_url
