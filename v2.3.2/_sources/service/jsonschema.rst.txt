.. _jsonschema:

The RCS JSON Schema
===================

RCS uses a JSON schema to validate registration requests (see :ref:`contract`).
The schema is written against draft 04 of `JSON Schema
<http://json-schema.org/>`_ and is reproduced below:

.. literalinclude:: ../../schemas/rcs_reg_schema_v2_0_0.json
    :language: javascript
    :linenos:

A sample request:

.. code-block:: javascript

  {
    "version": "2.0",
  	"fr": {
  		"service_url": "http://section917.cloudapp.net/arcgis/rest/services/TestData/ClassBreaks/MapServer/0",
  		"service_type": "esriFeature",
  		"service_name": "Sea Parks",
          "metadata": {
              "catalogue_url": "https://gcgeo.gc.ca/geonetwork/metadata/fra/ce7873ff-fbc0-4864-946e-6a1b4d739154",
              "metadata_url": "https://gcgeo.gc.ca/geonetwork/srv/fra/xml.metadata.download?uuid=ce7873ff-fbc0-4864-946e-6a1b4d739154&fromWorkspace="
          }
  	},
  	"en": {
  		"service_url": "http://section917.cloudapp.net/arcgis/rest/services/TestData/ClassBreaks/MapServer/0",
  		"service_type": "esriFeature",
  		"service_name": "Sea Parks",
          "metadata": {
              "catalogue_url": "https://gcgeo.gc.ca/geonetwork/metadata/eng/ce7873ff-fbc0-4864-946e-6a1b4d739154",
              "metadata_url": "https://gcgeo.gc.ca/geonetwork/srv/eng/xml.metadata.download?uuid=ce7873ff-fbc0-4864-946e-6a1b4d739154&fromWorkspace="
          }
  	}
  }
