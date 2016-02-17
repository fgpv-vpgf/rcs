# -*- coding: utf-8 -*-
"""
Tests RCS request signatures for validity
"""
from __future__ import division, print_function, unicode_literals

import hashlib, hmac, base64, logging, flask, iso8601, datetime, services.db

from flask.ext.restful import abort
from functools import wraps


def get_logger():
    """This function does not deserve a comment"""
    return flask.current_app.logger


def sign(key, *parts):
    """
    Creates an HMAC_SHA256 signature from a key and a set of message parts

    :param key: The signing key to use
    :type key: str
    :returns: str -- a URL safe base64 encoded signature
    """
    u8parts = [p.encode('utf8') for p in parts]
    msg = str('').join(u8parts)
    logging.debug(msg)
    h = hmac.new(str(key), msg, digestmod=hashlib.sha256)
    return base64.urlsafe_b64encode(h.digest()).replace('=', '')


def test_request(request):
    """
    Test the signature of a given request.

    Pulls the signature components from the request and generates a reference signature.
    Tests if the reference signature matches the Authorization header in the request.

    :param request: A flask request object containing the request to validate
    :returns: bool -- if the generated signature matches the authorization header
    """
    logger = get_logger()
    for h in 'Authorization TimeStamp Sender'.split():
        logger.debug(h + ': ' + request.headers.get(h, 'MISSING'))
    dt = request.headers.get('TimeStamp', None)
    cid = request.headers.get('Sender', None)
    msg_sig = request.headers.get('Authorization', None)
    if not (dt and cid and msg_sig):
        logger.warning('Missing data from headers, sig check failed')
        return False
    rqpath = request.path
    rqbody = request.data
    psk = services.db.auth.get_key(cid)

    ref_sig = sign(psk, rqpath, cid, dt, rqbody)
    logger.info('Signature received: {0}  ##  Signature generated: {1}'.format(msg_sig, ref_sig))
    return ref_sig is not None and ref_sig == msg_sig


def validate(func):
    """
    Wraps a service endpoint and checks the authentication headers.

    Tests the signature on the request and ensures the request time is current.
    Failure results in a 401 HTTP error if SIG_CHECK is enabled, if not validation
    will always pass.
    """
    def validation_fail(msg):
        if flask.current_app.config['SIG_CHECK']:
            abort(401, msg=msg)
        else:
            # be vocal if SIG_CHECK is accidentally set to False in production
            get_logger().warning('Authorization failure [{0}] ignored: SIG_CHECK is off in the config'.format(msg))

    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not test_request(flask.request):
            validation_fail('Invalid signature')
        try:
            if not check_time(flask.request):
                validation_fail('Request time out of sync')
        except iso8601.ParseError:
            if flask.current_app.config['SIG_CHECK']:
                abort(400, msg="Unparsable timestamp")
            else:
                get_logger().warning('Timestamp parse failure ignored: SIG_CHECK is off in the config')
        return func(*args, **kwargs)
    return decorated_function


def check_time(request):
    """
    Ensure the sent time is within 2 minutes of the current time

    :param sent: An ISO8601 encoded date
    :type sent: str
    :raises: ParseError -- if the datetime cannot be parsed
    :returns: bool -- sent time is within 2 minutes of the current time
    """
    logger = get_logger()
    sent = request.headers.get('TimeStamp')
    dt = iso8601.parse_date(sent)
    now = datetime.datetime.now(iso8601.iso8601.Utc())
    two_min = datetime.timedelta(minutes=2)
    logger.info('Header date: {0}  ##  Current timestamp: {1}'.format(sent, now))
    return -two_min < now-dt < two_min


if __name__ == '__main__':
    dt = '2007-01-25T12:00:00Z'
    psk = 'test'
    cid = '1'
    rqpath = '/register/22'
    rqbody = '{"a":1}'
    sig = sign(psk, rqpath, cid, dt, rqbody)
    print(sig)
    REQUEST_PATH = '/register/23ax5t'
    SENDER_ID = 'jstest'
    TIME_STAMP = '2014-12-05T18:28:56.714Z'
    REQUEST_BODY = '''{"version":"1.0.0","payload_type":"wms","en":{"service_url":"http://wms.ess-ws.nrcan.gc.ca/wms/toporama_en","service_name":"Key Areas for Birds in Coastal Regions of the Canadian Beaufort Sea - la Mue ou l'élevage des couvées (de la mi-juillet à la mi-août)","layer":"limits"},"fr":{"service_url":"http://wms.ess-ws.nrcan.gc.ca/wms/toporama_en","layer":"limits"}}'''  # NOQA
    psk = 'test_-k'
    sig = sign(psk, REQUEST_PATH, SENDER_ID, TIME_STAMP, REQUEST_BODY)
    print(sig)
