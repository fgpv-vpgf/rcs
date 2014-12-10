import unittest, regparse.metadata as md

config_1 = { 'METADATA_URL': 'http://www2.dmsolutions.ca/cgi-bin/mswfs_gmap?version=1.3.0&request=getcapabilities&service=' }
config_2 = { 'METADATA_URL': 'http://nowhere.example.com/' }
valid_url = { 'metadata': { 'url': 'http://www2.dmsolutions.ca/cgi-bin/mswfs_gmap?version=1.3.0&request=getcapabilities&service=wms' } }
valid_uuid = { 'metadata': { 'uuid': 'wms' } }

class MetadataTestCase(unittest.TestCase):

    def test_url(self):
        u = md.get_url( valid_url, config_1 )
        self.assertEquals( u, valid_url['metadata']['url'] )

    def test_uuid(self):
        u = md.get_url( valid_uuid, config_1 )
        self.assertEquals( u, valid_url['metadata']['url'] )

    def test_bad_config(self):
        with self.assertRaises( md.MetadataException ):
            md.get_url( valid_uuid, config_2 )

if __name__ == '__main__':
    unittest.main()
