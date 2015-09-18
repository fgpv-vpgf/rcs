RAMP Configuration Service
--------------------------

.. image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/fgpv-vpgf/rcs
   :target: https://gitter.im/fgpv-vpgf/rcs?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

The RAMP Configuration Service (RCS) is a web service designed to work with the
Reusable Accessible Mapping Platform `(RAMP) <http://ramp-pcar.github.io>`_ to support
loading of map layers from data catalogues.

RCS as a cache between data catalogues and the RAMP client application.  It will
prefetch data from certain endpoints and store them as configuration fragments
which the RAMP client can consume.  It is implemented as a REST service in
Python with a fairly minimal store and retrieve API.

RCS is developed by Environment Canada as part of the RAMP project and is licensed
under the MIT license.
