> *NOTE* The RCS code published to the github repository may not reflect the latest
> version of the contract.

# RAMP Configuration Service

The RAMP Configuration Service (RCS) is a web service designed to work with the
Reusable Accessible Mapping Platform [(RAMP)](http://ramp-pcar.github.io) to support
loading of map layers from data catalogues.

## Background

RCS as a cache between data catalogues and the RAMP client application.  It will
prefetch data from certain endpoints and store them as configuration fragments
which the RAMP client can consume.  It is implemented as a REST service in
Python with a fairly minimal store and retrieve API.

## Overview

### Development
1. [Development Setup](docs/devsetup.md)
1. [Building](docs/building.md)
1. [Service Contract](docs/contract.md)

### Deployment
1. [Deployment](deployment.md)
1. [Replication](replication.md)

## Functionality

RCS currently exposes three REST endpoints.

Endpoint | Description
-------- | -----------
GET /doc/[lang]/[smallkey] | Retrieves a single configuration fragment
GET /docs/[lang]/[smallkey]{,[smallkey]} | Retrieves multiple configuration fragments
PUT /register/[smallkey] | Stores a configuration fragment
DELETE /register/[smallkey] | Deletes a configuration fragment

The RAMP client is intended to call the GET driven endpoints for dynamically
loading layers.  These functions are intended to be extensible and also allow
for the retrieval of generic configuration as well.

The data catalogue is intended to call the PUT and DELETE endpoints for storing
data.  Currently registration will accept ESRI feature service endpoints and WMS
endpoints.

Full specifications of the service are still in development please see the
[current draft specification](docs/contract.md)
for more details.
