Service Quick Reference
=======================

RCS currently exposes 7 REST endpoints.

====================================================  ==================================================================
Endpoint                                              Description
====================================================  ==================================================================
GET /doc/[lang]/[key]                                 Retrieves a single configuration fragment
GET /docs/[lang]/[key]{,[key]}{/[sortarg]}            Retrieves multiple configuration fragments, sorted by geometry type if sortarg = sort
PUT /register/[key]                                   Stores a configuration fragment
DELETE /register/[key]                                Deletes a configuration fragment
PUT /register/refresh/[key]                           Stores a configuration fragment
POST /refresh/[args]                                  Refreshes existing records, use "all" or an integer specifying minimum age
POST /upgrade/[key]                                   Upgrades a registered v1 key to a v2 record
====================================================  ==================================================================

RCS also has 3 debug endpoints. These are enabled by setting the DEBUG_ENDPOINTS variable to True in config.py.

====================================================  ==================================================================
Endpoint                                              Description
====================================================  ==================================================================
GET /accesslog/[index]                                Retrieves the RCS access logs. [index] specifies the index of the log file if multiple exist
GET /log/[index]                                      Retrieves the error log for the RCS
GET /all_keys/[lang]                                  Displays a list of registered keys and their related service, by language
====================================================  ==================================================================

*NOTE: deprecated endpoints are not included in the summary*

The RAMP client is intended to call the GET driven endpoints for dynamically
loading layers.  These functions are intended to be extensible and also allow
for the retrieval of generic configuration as well.

The data catalogue is intended to call the PUT, POST and DELETE endpoints for storing
data.  Currently registration will accept ESRI feature service endpoints and WMS
endpoints.

More details are available on the :ref:`contract` page.
