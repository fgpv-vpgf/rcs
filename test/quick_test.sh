curl -X PUT http://localhost:6101/v2/register/test -H 'Content-type: application/json' -d '{"version":"2.0", "en":{"service_url":"http://wms.ess-ws.nrcan.gc.ca/wms/toporama_en?VERSION=1.1.1&request=GetCapabilities&service=wms"}, "fr":{"service_url":"http://wms.ess-ws.nrcan.gc.ca/wms/toporama_en?VERSION=1.1.1&request=GetCapabilities&service=wms"}}'

curl http://localhost:6101/v2/doc/en/test
echo
echo

curl -X PUT http://localhost:6101/v2/register/testsc -H 'Content-type: application/json' -d '{"version":"2.0", "en":{"service_url":"http://wms.ess-ws.nrcan.gc.ca/wms/toporama_en?VERSION=1.1.1&request=GetCapabilities&service=wms", "service_type":"ogcWms", "scrape_only": ["railway"]}, "fr":{"service_url":"http://wms.ess-ws.nrcan.gc.ca/wms/toporama_en?VERSION=1.1.1&request=GetCapabilities&service=wms"}}'

curl http://localhost:6101/v2/doc/en/testsc
curl http://localhost:6101/v1/doc/en/testsc
echo
echo

curl -X PUT http://localhost:6101/v2/register/feat -H 'Content-type: application/json' -d '{"version":"2.0", "en":{"service_url":"http://section917.cloudapp.net/arcgis/rest/services/JOSM/Oilsands_en/MapServer/1", "service_type":"esriFeature", "tolerance":99}, "fr":{"service_url":"http://section917.cloudapp.net/arcgis/rest/services/JOSM/Oilsands_en/MapServer/1", "service_type":"esriFeature", "tolerance":99}}'

curl http://localhost:6101/v2/doc/en/feat
echo
echo

curl -X PUT http://localhost:6101/v2/register/ms -H 'Content-type: application/json' -d '{"version":"2.0", "en":{"service_url":"http://section917.cloudapp.net/arcgis/rest/services/JOSM/Oilsands_en/MapServer"}, "fr":{"service_url":"http://section917.cloudapp.net/arcgis/rest/services/JOSM/Oilsands_en/MapServer/"}}'

curl http://localhost:6101/v2/doc/en/ms

# curl -X PUT http://localhost:6101/v2/register/23ax5t -H 'Authorization: v6XaQasyZzcm_Bz4W_p5fO1wbyJKCZnJFEspIXw9elY' -H 'TimeStamp: 2014-12-05T18:28:56.714Z' -H 'Sender: jstest' -H 'Content-Type: application/json' -d '{\"version\":\"1.0.0\",\"payload_type\":\"wms\",\"en\":{\"service_url\":\"http://wms.ess-ws.nrcan.gc.ca/wms/toporama_en\",\"layer\":\"limits\"},\"fr\":{\"service_url\":\"http://wms.ess-ws.nrcan.gc.ca/wms/toporama_en\",\"layer\":\"limits\"}}'
