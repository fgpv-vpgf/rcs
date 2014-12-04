"""
Tests RCS request signatures for validity
"""
from __future__ import division, print_function, unicode_literals
import hashlib, hmac, base64

def sign( key, *parts ):
    """
    Creates an HMAC_SHA256 signature from a key and a set of message parts

    :param key: The signing key to use
    :type key: str
    :returns: str -- a URL safe base64 encoded signature
    """
    msg = ''.join( parts )
    h = hmac.new( str(key), msg, digestmod=hashlib.sha256 )
    return base64.urlsafe_b64encode( h.digest() )

def check_time( sent ):
    """
    Ensure the sent time is within 2 minutes of the current time

    :param sent: An ISO8601 encoded date
    :type sent: str
    :returns: bool -- sent time is within 2 minutes of the current time
    """
    return False

if __name__ == '__main__':
    dt = '2007-01-25T12:00:00Z'
    psk = 'test'
    cid = '1'
    rqpath = '/register/22'
    rqbody = '{"a":1}'
    sig = sign( psk, rqpath, cid, dt, rqbody )
    print( sig )
