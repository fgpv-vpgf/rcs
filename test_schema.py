import json, os, pytest, requests, random
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

doc_sample_url_v11 = """
    {
        "version": "1.0.0",
        "payload_type": "wms",
        "en": {
            "service_url": "http://wms.ess-ws.nrcan.gc.ca/wms/toporama_en",
            "layer": "limits",
            "metadata": { "catalogue_url": "http://example.com", "metadata_url": "http://example.com" }
        },
        "fr": {
            "service_url": "http://wms.ess-ws.nrcan.gc.ca/wms/toporama_fr",
            "layer": "limits",
            "metadata": { "catalogue_url": "http://example.com", "metadata_url": "http://example.com" }
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

@pytest.fixture
def schema110():
    return json.load( open(os.path.join('schemas','rcs_reg_schema_v1_1_0.json')) )

@pytest.fixture
def schema100():
    return json.load( open(os.path.join('schemas','rcs_reg_schema_v1_0_0.json')) )

def test_doc_sample_forward_compat(schema110):
    fragment = json.loads( doc_sample_v1 )
    r = validate( fragment, schema110 )
    assert  r is None

def test_url_v11(schema110):
    fragment = json.loads( doc_sample_url_v11 )
    r = validate( fragment, schema110 )
    assert  r is None

def test_doc_sample_v11(schema110):
    fragment = json.loads( doc_sample_v11 )
    r = validate( fragment, schema110 )
    assert  r is None

def test_doc_sample_v1(schema100):
    fragment = json.loads( doc_sample_v1 )
    r = validate( fragment, schema100 )
    assert  r is None
