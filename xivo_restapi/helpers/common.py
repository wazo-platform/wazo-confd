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
from functools import wraps
from werkzeug.exceptions import HTTPException

from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_dao.data_handler.exception import MissingParametersError
from xivo_dao.data_handler.exception import InvalidParametersError
from xivo_dao.data_handler.exception import NonexistentParametersError
from xivo_dao.data_handler.exception import ElementAlreadyExistsError
from xivo_dao.data_handler.exception import ElementCreationError
from xivo_dao.data_handler.exception import ElementEditionError
from xivo_dao.data_handler.exception import ElementDeletionError
from xivo_dao.data_handler.exception import AssociationNotExistsError

from xivo_restapi.helpers import serializer


logger = logging.getLogger(__name__)


def exception_catcher(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        generic_errors = (MissingParametersError,
                          InvalidParametersError,
                          NonexistentParametersError,
                          ElementAlreadyExistsError,
                          ElementCreationError,
                          ElementEditionError,
                          ElementDeletionError)

        try:
            return func(*args, **kwargs)
        except generic_errors as e:
            return _make_response_encoded(e, 400)
        except ValueError, e:
            logger.exception(e)
            data = "No parsable data in the request, Be sure to send a valid JSON file"
            return _make_response_encoded(data, 400)
        except (ElementNotExistsError, AssociationNotExistsError) as e:
            return _make_response_encoded(e, 404)
        except HTTPException:
            raise
        except Exception as e:
            data = 'unexpected error during request: %s' % e
            return _make_response_encoded(data, 500, exc_info=True)
    return decorated_func


def _make_response_encoded(message, code, exc_info=False):
    logger.error(message, exc_info=exc_info)
    return make_response(serializer.encode([unicode(message)]), code)


class ParameterExtractor(object):

    NUMERIC = ('limit', 'skip')
    DIRECTIONS = ('asc', 'desc')

    def __init__(self, columns=None):
        self.columns = columns or []

    def extract(self, arguments):
        self._reset()

        for name in self.NUMERIC:
            self._extract_numeric(name, arguments)
        self._extract_direction(arguments)
        self._extract_order(arguments)
        self._extract_search(arguments)

        self._check_invalid()
        return self.extracted

    def _reset(self):
        self.invalid = []
        self.extracted = {}

    def _extract_numeric(self, name, arguments):
        value = arguments.get(name, None)
        if value:
            if value.isdigit() and int(value) > 0:
                self.extracted[name] = int(value)
            else:
                self.invalid.append("%s must be a postive integer" % name)

    def _extract_direction(self, arguments):
        if 'direction' in arguments:
            if arguments['direction'] in self.DIRECTIONS:
                self.extracted['direction'] = arguments['direction']
            else:
                self.invalid.append("direction must be asc or desc")

    def _extract_order(self, arguments):
        column_name = arguments.get('order', None)
        if column_name:
            if column_name in self.columns:
                self.extracted['order'] = column_name
            else:
                self.invalid.append("ordering column '%s' does not exist" % column_name)

    def _extract_search(self, arguments):
        if 'search' in arguments:
            self.extracted['search'] = arguments['search']

    def _check_invalid(self):
        if self.invalid:
            raise InvalidParametersError(self.invalid)


def extract_search_parameters(arguments, columns=None):
    return ParameterExtractor(columns).extract(arguments)
