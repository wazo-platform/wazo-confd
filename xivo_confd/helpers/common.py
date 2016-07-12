# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import logging
import json

from werkzeug.exceptions import HTTPException
from flask_restful.utils import http_status_message
from flask import g

from xivo_dao.helpers.db_manager import Session
from xivo_dao.helpers.exception import ServiceError
from xivo_dao.helpers.exception import NotFoundError

from xivo_confd.helpers.mooltiparse.errors import ValidationError
from xivo_confd.helpers.mooltiparse.errors import ContentTypeError


logger = logging.getLogger(__name__)

GENERIC_ERRORS = (ServiceError,
                  ValidationError,
                  ContentTypeError)

NOT_FOUND_ERRORS = (NotFoundError,)


def handle_error(error):
    rollback()

    exc_info = True
    code = 500

    if isinstance(error, NOT_FOUND_ERRORS):
        messages = [unicode(error)]
        code = 404
        exc_info = False
    elif isinstance(error, GENERIC_ERRORS):
        messages = [unicode(error)]
        code = 400
        exc_info = False
    elif isinstance(error, HTTPException):
        messages, code = extract_http_messages(error)
        exc_info = False
    else:
        messages = [u'Unexpected error: {}'.format(error)]

    logger.error(error, exc_info=exc_info)
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
        messages = ["Input Error - {}: {}".format(key, value)
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
