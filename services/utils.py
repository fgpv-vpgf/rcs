"""
API utilities
"""
from functools import wraps
from flask import current_app, request


def log_exception(sender, exception):
    """
    Detailed error logging function.  Designed to attach to Flask exception
    events and logs a bit of extra infomration about the request that triggered
    the exception.

    :param sender: The sender for the exception (we don't use this and log everyhing against app right now)
    :param exception: The exception that was triggered
    :type exception: Exception
    """
    current_app.logger.error(
        """
Request:   {method} {path}
IP:        {ip}
Raw Agent: {agent}
        """.format(
            method=request.method,
            path=request.path,
            ip=request.remote_addr,
            agent=request.user_agent.string,
        ), exc_info=exception
    )


def jsonp(func):
    """
    A decorator function that wraps JSONified output for JSONP requests.
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function
