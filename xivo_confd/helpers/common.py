# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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
from xivo_dao.helpers import errors
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
    # we need to keep error messages compatiable with API v1.1,
    # but flask-restful's error handling isn't flexible
    # enough to allow us to reformat its error messages.
    # So we attempt to extract the errors from the exception
    data = getattr(error, 'data', {})
    message = data.get('message', None)
    if isinstance(message, dict):
        code = error.code
        messages = ["Input Error - {}: {}".format(key, value)
                    for key, value in message.iteritems()]
    else:
        # Return a generic HTTP error message if we couldn't find anything
        code = getattr(error, 'code', 400)
        messages = [getattr(error, 'description', http_status_message(code))]

    return messages, code


def error_response(messages, code):
    response = json.dumps(messages)
    return (response, code, {'Content-Type': 'application/json'})


class ParameterExtractor(object):

    PARAMETERS = ('search', 'direction', 'order')
    NUMERIC = ('limit', 'skip', 'offset')
    DIRECTIONS = ('asc', 'desc')

    def __init__(self, extra):
        self.extra = extra

    def extract(self, arguments):
        self._reset()

        for name in self.NUMERIC:
            self._extract_numeric(name, arguments)

        all_parameters = self.PARAMETERS + tuple(self.extra)
        for parameter in all_parameters:
            self._extract_parameter(parameter, arguments)

        self._validate_direction()

        return self.extracted

    def _reset(self):
        self.extracted = {}

    def _extract_numeric(self, name, arguments):
        value = arguments.get(name, None)
        if value:
            if not value.isdigit():
                raise errors.wrong_type(name, 'positive number')
            value = int(value)
            if value < 0:
                raise errors.wrong_type(name, 'positive number')
            self.extracted[name] = value

    def _extract_parameter(self, name, arguments):
        if name in arguments:
            self.extracted[name] = arguments[name]

    def _validate_direction(self):
        if 'direction' in self.extracted:
            if self.extracted['direction'] not in self.DIRECTIONS:
                raise errors.invalid_direction()


def extract_search_parameters(arguments, extra=None):
    extra = extra or []
    return ParameterExtractor(extra).extract(arguments)
