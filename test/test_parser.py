import pytest, regparse.metadata as md

config_1 = {'METADATA_URL': 'http://www2.dmsolutions.ca/cgi-bin/mswfs_gmap?version=1.3.0&request=getcapabilities&service={0}', 'CATALOGUE_URL': 'http://www.google.ca/'}  # NOQA
config_2 = {'METADATA_URL': 'http://nowhere.example.com/{0}', 'CATALOGUE_URL': "{0}"}
valid_url = {'metadata': {'metadata_url': 'http://www2.dmsolutions.ca/cgi-bin/mswfs_gmap?version=1.3.0&request=getcapabilities&service=wms', 'catalogue_url': 'http://www.google.ca/'}}  # NOQA
valid_uuid = {'metadata': {'uuid': 'wms'}}


@pytest.mark.xfail
def test_url():
    u, c = md.get_url(valid_url, config_1)
    assert u == valid_url['metadata']['metadata_url']


@pytest.mark.xfail
def test_uuid():
    u, c = md.get_url(valid_uuid, config_1)
    assert u == valid_url['metadata']['metadata_url']


def test_bad_config():
    with pytest.raises(md.MetadataException):
        md.get_url(valid_uuid, config_2)
