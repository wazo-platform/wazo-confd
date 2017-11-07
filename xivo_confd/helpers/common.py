# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

import logging
import json

from werkzeug.exceptions import HTTPException
from flask_restful.utils import http_status_message
from flask import g

from xivo_dao.helpers.db_manager import Session
from xivo_dao.helpers.exception import ServiceError
from xivo_dao.helpers.exception import NotFoundError

logger = logging.getLogger(__name__)

GENERIC_ERRORS = (ServiceError,)

NOT_FOUND_ERRORS = (NotFoundError,)


def handle_error(error):
    rollback()

    exc_info = True
    code = 500

    try:
        error_message = unicode(error)
    except UnicodeDecodeError:
        error_message = str(error).decode('utf-8', errors='replace')

    if isinstance(error, NOT_FOUND_ERRORS):
        messages = [error_message]
        code = 404
        exc_info = False
    elif isinstance(error, GENERIC_ERRORS):
        messages = [error_message]
        code = 400
        exc_info = False
    elif isinstance(error, HTTPException):
        messages, code = extract_http_messages(error)
        exc_info = False
    else:
        messages = [u'Unexpected error: {}'.format(error_message)]

    logger.error(error_message, exc_info=exc_info)
    return error_response(messages, code)


def rollback():
    Session.rollback()

    sysconfd = g.get('sysconfd_publisher')
    if sysconfd:
        sysconfd.rollback()

    bus = g.get('bus_publisher')
    if bus:
        bus.rollback()


def extract_http_messages(error):
    # we need to keep error messages compatible with API v1.1,
    # but flask-restful's error handling isn't flexible
    # enough to allow us to reformat its error messages.
    # So we attempt to extract the errors from the exception
    data = getattr(error, 'data', {})
    message = data.get('message', None)
    if isinstance(message, dict):
        code = error.code
        messages = [u"Input Error - {}: {}".format(key, value)
                    for key, value in message.iteritems()]
    elif isinstance(message, unicode):
        code = error.code
        messages = [message]
    else:
        # Return a generic HTTP error message if we couldn't find anything
        code = getattr(error, 'code', 400)
        messages = [getattr(error, 'description', http_status_message(code))]

    return messages, code


def error_response(messages, code):
    response = json.dumps(messages)
    return (response, code, {'Content-Type': 'application/json'})
