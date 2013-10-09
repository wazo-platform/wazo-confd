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

from xivo_dao.data_handler.exception import MissingParametersError, \
    InvalidParametersError, ElementAlreadyExistsError, ElementNotExistsError, \
    ElementCreationError, ElementDeletionError, ElementEditionError, NonexistentParametersError
from xivo_restapi.helpers import serializer
from flask.globals import request


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
        except ElementNotExistsError, e:
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


DIRECTIONS = ['asc', 'desc']


def extract_find_parameters(ordering):
    invalid = []
    parameters = {}

    if 'limit' in request.args:
        limit = request.args['limit']
        if limit.isdigit() and int(limit) > 0:
            parameters['limit'] = int(limit)
        else:
            invalid.append("limit must be a positive integer")

    if 'skip' in request.args:
        skip = request.args['skip']
        if skip.isdigit() and int(skip) >= 0:
            parameters['skip'] = int(skip)
        else:
            invalid.append("skip must be a positive integer")

    if 'order' in request.args:
        column_name = request.args['order']
        if column_name in ordering:
            parameters['order'] = ordering[column_name]
        else:
            invalid.append("ordering column '%s' does not exist" % column_name)

    if 'direction' in request.args:
        direction = request.args['direction']
        if direction in DIRECTIONS:
            parameters['direction'] = direction
        else:
            invalid.append("direction must be asc or desc")

    if 'search' in request.args:
        parameters['search'] = request.args['search']

    if len(invalid) > 0:
        raise InvalidParametersError(invalid)

    return parameters
