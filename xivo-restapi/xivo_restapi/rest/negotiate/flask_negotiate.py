#Modified by Avencall:
#If the "Accept" header is not present, the returned content type
#is supposed to be supported

from flask import request
from functools import wraps
from werkzeug.exceptions import UnsupportedMediaType, NotAcceptable
import logging

logger = logging.getLogger()


def consumes(*content_types):
    def decorated(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if request.mimetype not in content_types:
                raise UnsupportedMediaType()
            return fn(*args, **kwargs)
        return wrapper
    return decorated


def produces(*content_types):
    def decorated(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            requested = set(request.accept_mimetypes.values())
            requested.discard('*/*')
            logger.debug(str(requested))
            defined = set(content_types)
            if len(requested) > 0 and len(requested & defined) == 0:
                raise NotAcceptable()
            return fn(*args, **kwargs)
        return wrapper
    return decorated
