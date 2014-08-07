# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from flask.helpers import make_response
from werkzeug.exceptions import HTTPException

from xivo_dao.data_handler import errors
from xivo_dao.data_handler.exception import ServiceError
from xivo_dao.data_handler.exception import NotFoundError

from xivo_restapi.helpers.mooltiparse.errors import ValidationError
from xivo_restapi.helpers.mooltiparse.errors import ContentTypeError

from xivo_restapi.helpers import serializer


logger = logging.getLogger(__name__)

GENERIC_ERRORS = (ServiceError,
                  ValidationError,
                  ContentTypeError)

NOT_FOUND_ERRORS = (NotFoundError,)


def make_error_response(error):
    if isinstance(error, NOT_FOUND_ERRORS):
        return _make_response_encoded(error, 404)
    elif isinstance(error, GENERIC_ERRORS):
        return _make_response_encoded(error, 400)
    elif isinstance(error, HTTPException):
        raise error
    else:
        message = 'Unexpected error: %s' % error
        return _make_response_encoded(message, 500, exc_info=True)


def _make_response_encoded(message, code, exc_info=False):
    logger.error(message, exc_info=exc_info)
    return make_response(serializer.encode([unicode(message)]), code)


class ParameterExtractor(object):

    PARAMETERS = ('search', 'direction', 'order')
    NUMERIC = ('limit', 'skip')

    def __init__(self, extra):
        self.extra = extra

    def extract(self, arguments):
        self._reset()

        for name in self.NUMERIC:
            self._extract_numeric(name, arguments)

        all_parameters = self.PARAMETERS + tuple(self.extra)
        for parameter in all_parameters:
            self._extract_parameter(parameter, arguments)

        return self.extracted

    def _reset(self):
        self.extracted = {}

    def _extract_numeric(self, name, arguments):
        value = arguments.get(name, None)
        if value:
            if not value.isdigit():
                raise errors.wrong_type(name, '')
            self.extracted[name] = int(value)

    def _extract_parameter(self, name, arguments):
        if name in arguments:
            self.extracted[name] = arguments[name]


def extract_search_parameters(arguments, extra=None):
    extra = extra or []
    return ParameterExtractor(extra).extract(arguments)
