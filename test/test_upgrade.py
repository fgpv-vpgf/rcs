from services.upgrade import wms_upgrade, feat_upgrade


def test_wms_basic():
    v1_req = {'service_url': 'http://localhost/', 'layer': 'l'}
    v2 = wms_upgrade(v1_req)
    assert len(v2['scrape_only']) == 1
    assert v2['scrape_only'][0] == 'l'
    assert v2['service_type'] == 'ogcWms'


def test_feat_basic():
    v1_req = {'service_url': 'http://localhost/', 'display_field': 'test'}
    v2 = feat_upgrade(v1_req)
    assert v2['display_field'] == 'test'
    assert v2['service_type'] == 'esriFeature'
