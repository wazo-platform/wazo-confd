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

        self._check_invalid()
        return self.extracted

    def _reset(self):
        self.invalid = []
        self.extracted = {}

    def _extract_numeric(self, name, arguments):
        value = arguments.get(name, None)
        if value:
            if value.isdigit():
                self.extracted[name] = int(value)
            else:
                self.invalid.append("%s must be only digits" % name)

    def _extract_parameter(self, name, arguments):
        if name in arguments:
            self.extracted[name] = arguments[name]

    def _check_invalid(self):
        if self.invalid:
            raise InvalidParametersError(self.invalid)


def extract_search_parameters(arguments, extra=None):
    extra = extra or []
    return ParameterExtractor(extra).extract(arguments)
