RAMP Configuration Service
--------------------------

The RAMP Configuration Service (RCS) is a web service designed to work with the
Reusable Accessible Mapping Platform `(RAMP) <http://ramp-pcar.github.io>`_ to support
loading of map layers from data catalogues.

RCS as a cache between data catalogues and the RAMP client application.  It will
prefetch data from certain endpoints and store them as configuration fragments
which the RAMP client can consume.  It is implemented as a REST service in
Python with a fairly minimal store and retrieve API.

RCS is developed by Environment Canada as part of the RAMP project and is lisenced
under the MIT license.
