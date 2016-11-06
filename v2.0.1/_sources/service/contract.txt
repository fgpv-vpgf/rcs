.. _contract:

RCS v2 Service Contract
=======================

This release of RCS publishes endpoints at ``/v2``.  The
endpoints at ``/v2`` are compatible with registration requests for schema
version 2.0 and document requests for RAMP version 2 (in support of Federal
Geospatial Platform's R2 Visualization requirements).

The current JSON schema is used to validate registration requests is at:

.. toctree::

    jsonschema

An older schema for RAMP versions prior to schema 1.0 is documented at:

.. toctree::

    endpoint_10

GET ``/v2/doc/[lang]/[key]``
---------------------------------

Success Code: 200

Request Body: Empty

Response Body: JSON Object

The response will have a JSON configuration fragment to be merged into the RAMP
configuration.  It will be compatible with RAMP schema 2.0, although as it is a
fragment it will not validate against the schema without additional
configuration being supplied.

Error conditions:

- invalid language code: 400 Bad Request, response body empty
- key not found: 404 Not Found, response body empty

GET ``/v2/docs/[lang]/[key]{,[key]}{/[sortarg]}``
-----------------------------------------------------------

Success Code: 200

Request Body: Empty

Response Body: JSON Array

The response will be an array of JSON objects, each object will be a JSON
configuration fragment to be merged into the RAMP config.  It will be
compatible with RAMP schema 1.0, although as it is a fragment it will not
validate against the schema without additional configuration being supplied.

Error conditions:

- invalid language code: 400 Bad Request, response body empty
- key not found: 200 normal response, the corresponding fragment will be
  structured as:
  ``{"error_code":404,"key":"[key]"}``

PUT ``/v2/register/[key]``
-------------------------------

Success Code: 201

Request Body: JSON Object

Request Headers: Implement the :ref:`signing` protocol

Response Body: Empty

Error Conditions:

- payload does not conform to schema: 400 Bad Request, body contains
  ``{"errors":["message 1","message 2"]}``
- invalid timestamp format: 400 Bad Request
- unable to verify metadata surce: 400 Bad Request
- missing headers / unretrivable key: 401 Not Authorized
- exception in processing: 500 Internal Server Error, empty body

Registration requests are validated against
The body of the request should conform to:

.. code-block:: javascript

    {"version":"2.0","en":(payload),"fr":(payload) }

Payload Type ``basic``
^^^^^^^^^^^^^^^^^^^^^^^^

The basic payload describes elements common to all registered services, and is not a
service type unto itself:

.. code-block:: javascript

    {
        "service_url": (str: URL to ESRI REST Feature Layer Endpoint),
        "metadata": {
            "uuid": (str: a unique identifier),
            "catalogue_url": (str: URL describing the layer in full detail)
            "metadata_url": (str: direct URL to metadata for that layer)
        }
    }

- the service URL should not have any query string component
- ``metadata`` is optional
- where ``service_url`` specifies Feature Layer endpoint, this may be an
  endpoint from a *Feature Service* or a *Map Service*; what is important is
  that the URL should reference the layer id within it
- *NOTE metadata should be present for most layers, it is left as optional
  only for exceptional cases*
- one of ``uuid`` or ``*_url`` should be specified
- ``metadata_url`` should be direct URL to the layer's metadata which should be in XML format
- ``catalogue_url`` should be a URL linking back to the catalogue's page describing the layer
- ``uuid`` should be a unique identifier which can be prefixed with a preconfigured metadata URL to retrieve specific metadata for that layer.


Payload Type ``feature``
^^^^^^^^^^^^^^^^^^^^^^^^

The feature payload should conform to:

.. code-block:: javascript

    {
        "service_url": (str: URL to ESRI REST Feature Layer Endpoint),
        "service_type": (str: Type of Esri Feature service),
        "service_name": (str: Layer Name),
        "display_field": (str: Default attribute for identifying features),
        "loading_mode": (str: Specifies the layer loading mode: either snapshot -
        load all data upfront, or ondemand load data as needed),
        "max_allowable_offset": (int: Simplification factor for the layer geometry;
        may be omitted in which case no value will be provided in the output
        leaving the viewer to apply its own logic.),
        "tolerance": (int: Tolerance, in pixels, of feature queries),
        "metadata": {
            "uuid": (str: a unique identifier),
            "catalogue_url": (str: URL describing the layer in full detail)
            "metadata_url": (str: direct URL to metadata for that layer)
        }
    }

- the service URL should not have any query string component
- ``metadata``, ``display_field``, ``service_name``, ``loading_mode``, ``max_allowable_offset``, ``tolerance`` are optional
- where ``service_url`` specifies Feature Layer endpoint, this may be an endpoint from a *Feature Service* or a *Map Service*; what is important is that the URL should reference the layer id within it


Payload Type ``imagery``
^^^^^^^^^^^^^^^^^^^^^^^^

The imagery service payload should conform to:

.. code-block:: javascript

  {
      "service_url": (str: URL to ESRI REST Feature Layer Endpoint),
      "service_type": (str: Type of Esri Imagery service, esriTile or esriImage),
      "service_name": (str: Layer Name),
      "metadata": {
          "uuid": (str: a unique identifier),
          "catalogue_url": (str: URL describing the layer in full detail)
          "metadata_url": (str: direct URL to metadata for that layer)
      }
  }

- the service URL should not have any query string component


Payload Type ``ogc wms``
^^^^^^^^^^^^^^^^^^^^^^^^

The wms payload should conform to:

.. code-block:: javascript

    {
        "service_url": (str: URL to WMS Service),
        "service_name": (str: Name of the service endpoint, used for display),
        "service_type": (str: Service type of the endpoint, ogcWms (support for ogcWmts may come at a later date)),
        "scrape_only": (str array: Indicates which layer entries should be scraped,
        all layers should be identified by their Name element.),
        "recursive": (bool: Indicates if children should be scraped and made available
        as individual layers to the viewer),
        "legend_format": (str: MIME type)",
        "feature_info_type": (str: MIME type, limited to "text/html;fgpv=summary", "text/html", "text/plain", "application/json"),
        "metadata": {
            "uuid": (str: a unique identifier),
            "catalogue_url": (str: URL describing the layer in full detail)
            "metadata_url": (str: direct URL to metadata for that layer)
        }
    }

- the service URL should not have any query string component
- ``service_name``, ``scrape_only``, ``metadata`` are optional


Payload Type ``esri map``
^^^^^^^^^^^^^^^^^^^^^^^^^

The esri map service (grouped layers) payload should conform to:

.. code-block:: javascript

    {
        "service_url": (str: URL to WMS Service),
        "service_name": (str: Name of the service endpoint, used for display),
        "service_type": (str: Service type of the endpoint, either esriMapServer
        or esriFeatureServer),
        "scrape_only": (int array: Indicates which layer entries should be scraped,
        all layers should be identified by their Name element.),
        "recursive": (bool: Indicates if children should be scraped and made available
        as individual layers to the viewer),
        "metadata": {
            "uuid": (str: a unique identifier),
            "catalogue_url": (str: URL describing the layer in full detail)
            "metadata_url": (str: direct URL to metadata for that layer)
        }
    }

- the service URL should not have any query string component
- ``service_name``, ``scrape_only``, ``metadata``, ``recursive``,  are optional


DELETE ``/v2/register/[key]``
----------------------------------

Success Code: 204

Request Body: Empty

Request Headers: Implement the :ref:`signing` protocol

Response Body: Empty

Error Conditions:

- key not found: 404 Not Found
- invalid timestamp format: 400 Bad Request
- missing headers / unretrivable key: 401 Not Authorized
- exception in processing: 500 Internal Server Error, empty body

POST ``/v2/upgrade/[key]``
--------------------------

Success Code: 200

Request Body: Empty

Request Headers: Implement the :ref:`signing` protocol

Request Params: key for an already registered v1 layer

Response Body: ``{ "success": ["key", …], "errors": {"key": "message", …} }``

Error conditions:

- Record not found in database: Upgrade failed 404
- Already upgraded

POST ``/v2/refresh/[params]``
-----------------------------

Success Code: 200

Request Body: JSON Object

Request Headers: Implement the :ref:`signing` protocol

Request Params: Either 'all' or a positive integer indicating the minimum age
in days of a record before it should be updated

Response Body: ``{"updated":["0"],"errors":{},"limit_reached":false}``



RCS v1 Endpoints
================

v1 registration of services, as well as simplification and updatefeature endpoints
have been deprecated in favour of v2.

The current JSON schema is used to validate registration requests is at:

.. toctree::

    jsonschema

An older schema for RAMP versions prior to schema 1.0 is documented at:

.. toctree::

    endpoint_09

GET ``/v1/doc/[lang]/[key]``
---------------------------------

Success Code: 200

Request Body: Empty

Response Body: JSON Object

The response will have a JSON configuration fragment to be merged into the RAMP
configuration.  It will be compatible with RAMP schema 1.0, although as it is a
fragment it will not validate against the schema without additional
configuration being supplied.

Error conditions:

- invalid language code: 400 Bad Request, response body empty
- key not found: 404 Not Found, response body empty

GET ``/v1/docs/[lang]/[key]{,[key]}{/[sortarg]}``
-------------------------------------------------

Success Code: 200

Request Body: Empty

Response Body: JSON Array

The response will be an array of JSON objects, each object will be a JSON
configuration fragment to be merged into the RAMP config.  It will be
compatible with RAMP schema 1.0, although as it is a fragment it will not
validate against the schema without additional configuration being supplied.

Error conditions:

- invalid language code: 400 Bad Request, response body empty
- key not found: 200 normal response, the corresponding fragment will be
  structured as:
  ``{"error_code":404,"key":"[key]"}``


DELETE ``/v1/register/[key]``
-----------------------------

Success Code: 204

Request Body: Empty

Request Headers: Implement the :ref:`signing` protocol

Response Body: Empty

Error Conditions:

- key not found: 404 Not Found
- invalid timestamp format: 400 Bad Request
- missing headers / unretrivable key: 401 Not Authorized
- exception in processing: 500 Internal Server Error, empty body
