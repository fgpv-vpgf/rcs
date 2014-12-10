import json, os, unittest, requests, random
from jsonschema import validate, ValidationError

doc_sample_v11 = """
    {
        "version": "1.0.0",
        "payload_type": "wms",
        "en": {
            "service_url": "http://wms.ess-ws.nrcan.gc.ca/wms/toporama_en",
            "layer": "limits",
            "metadata": { "uuid": "7" }
        },
        "fr": {
            "service_url": "http://wms.ess-ws.nrcan.gc.ca/wms/toporama_fr",
            "layer": "limits",
            "metadata": { "uuid": "7" }
        }
    }
"""

doc_sample_v1 = """
    {
        "version": "1.0.0",
        "payload_type": "wms",
        "en": {
            "service_url": "http://wms.ess-ws.nrcan.gc.ca/wms/toporama_en",
            "layer": "limits"
        },
        "fr": {
            "service_url": "http://wms.ess-ws.nrcan.gc.ca/wms/toporama_fr",
            "layer": "limits"
        }
    }
"""

class SchemaTestCase(unittest.TestCase):

    def setUp(self):
        self.schema110 = json.load( open(os.path.join('schemas','rcs_reg_schema_v1_1_0.json')) )
        self.schema100 = json.load( open(os.path.join('schemas','rcs_reg_schema_v1_0_0.json')) )

    def test_doc_sample_forward_compat(self):
        fragment = json.loads( doc_sample_v1 )
        r = validate( fragment, self.schema110 )
        self.assertEquals( r, None )

    def test_doc_sample_v11(self):
        fragment = json.loads( doc_sample_v11 )
        r = validate( fragment, self.schema110 )
        self.assertEquals( r, None )

    def test_doc_sample_v1(self):
        fragment = json.loads( doc_sample_v1 )
        r = validate( fragment, self.schema100 )
        self.assertEquals( r, None )

if __name__ == '__main__':
    unittest.main()
