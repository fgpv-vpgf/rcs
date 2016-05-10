curl -X PUT http://localhost:6101/v2/register/test -H 'Content-type: application/json' -d '{"version":"2.0", "en":{"service_url":"http://wms.ess-ws.nrcan.gc.ca/wms/toporama_en?VERSION=1.1.1&request=GetCapabilities&service=wms"}, "fr":{"service_url":"http://wms.ess-ws.nrcan.gc.ca/wms/toporama_en?VERSION=1.1.1&request=GetCapabilities&service=wms"}}'

curl http://localhost:6101/v2/doc/en/test
echo
echo

curl -X PUT http://localhost:6101/v2/register/test -H 'Content-type: application/json' -d '{ "fr": { "feature_info_format": "text/plain", "service_url": "http://wms.ess-ws.nrcan.gc.ca/wms/toporama_fr", "service_type": "ogcWms", "legend_format": "image/gif", "scrape_only": [ "frontieres" ], "service_name": "WMS french" }, "en": { "feature_info_format": "text/plain", "service_url": "http://wms.ess-ws.nrcan.gc.ca/wms/toporama_en", "service_type": "ogcWms", "legend_format": "image/gif", "scrape_only": [ "structures" ], "service_name": "WMS english" }, "version": "2.0" }'
curl http://localhost:6101/v2/doc/en/test
curl -X DELETE http://localhost:6101/v2/register/test
curl http://localhost:6101/v2/doc/en/test
curl -X DELETE http://localhost:6101/v2/register/test
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
echo
echo

curl -i -X PUT -H "Content-Type:application/json" http://localhost:6101/v2/register/image -d '{"fr":{"service_url":"http://www.agr.gc.ca/atlas/rest/services/imageservices/mb_colour_orthos_50cm/ImageServer","service_type":"esriImage","service_name":"Image french"},"en":{"service_url":"http://www.agr.gc.ca/atlas/rest/services/imageservices/mb_colour_orthos_50cm/ImageServer","service_type":"esriImage","service_name":"Image english"},"version":"2.0"}'
curl http://localhost:6101/v2/doc/en/image
echo
echo

curl -i -X PUT -H "Content-Type:application/json" http://localhost:6101/v2/register/geogratis -d '{"fr":{"feature_info_format":"text/plain","service_url":"http://maps.geogratis.gc.ca/wms/np_nmca_en","service_type":"ogcWms","legend_format":"image/gif","scrape_only":["national_marine_conservation_areas"],"service_name":"WMS french"},"en":{"feature_info_format":"text/plain","service_url":"http://maps.geogratis.gc.ca/wms/np_nmca_en","service_type":"ogcWms","legend_format":"image/gif","scrape_only":["national_marine_conservation_areas"],"service_name":"WMS english"},"version":"2.0"}'
curl http://localhost:6101/v2/doc/en/geogratis
echo
echo


# curl -X PUT http://localhost:6101/v2/register/23ax5t -H 'Authorization: v6XaQasyZzcm_Bz4W_p5fO1wbyJKCZnJFEspIXw9elY' -H 'TimeStamp: 2014-12-05T18:28:56.714Z' -H 'Sender: jstest' -H 'Content-Type: application/json' -d '{\"version\":\"1.0.0\",\"payload_type\":\"wms\",\"en\":{\"service_url\":\"http://wms.ess-ws.nrcan.gc.ca/wms/toporama_en\",\"layer\":\"limits\"},\"fr\":{\"service_url\":\"http://wms.ess-ws.nrcan.gc.ca/wms/toporama_en\",\"layer\":\"limits\"}}'
