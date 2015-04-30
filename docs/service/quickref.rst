Service Quick Reference
=======================

RCS currently exposes 6 REST endpoints.

========================================  ==================================================================
Endpoint                                  Description
========================================  ==================================================================
GET /doc/[lang]/[smallkey]                Retrieves a single configuration fragment
GET /docs/[lang]/[smallkey]{,[smallkey]}  Retrieves multiple configuration fragments
PUT /register/[smallkey]                  Stores a configuration fragment
DELETE /register/[smallkey]               Deletes a configuration fragment
POST /update/[age]                        Updates all cached fragements older than [age] days
PUT /updatefeature/[smallkey]             Merge a configuration fragment with an existing ESRI Feature Layer
========================================  ==================================================================

*NOTE: deprecated endpoints are not included in the summary*

The RAMP client is intended to call the GET driven endpoints for dynamically
loading layers.  These functions are intended to be extensible and also allow
for the retrieval of generic configuration as well.

The data catalogue is intended to call the PUT, POST and DELETE endpoints for storing
data.  Currently registration will accept ESRI feature service endpoints and WMS
endpoints.

More details are available on the :ref:`contract` page.
