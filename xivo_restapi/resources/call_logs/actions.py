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
from datetime import datetime
from flask import Blueprint
from flask.globals import request
from flask.helpers import make_response
from xivo_dao.data_handler.call_log import services
from xivo_dao.data_handler.exception import InvalidParametersError
from xivo_restapi import config
from xivo_restapi.authentication import auth
from xivo_restapi.helpers.common import exception_catcher
from xivo_restapi.negotiate.flask_negotiate import produces
from xivo_restapi.resources.call_logs import serializer
from xivo_restapi.resources.call_logs import mapper

logger = logging.getLogger(__name__)
blueprint = Blueprint('call_logs', __name__, url_prefix='/%s/call_logs' % config.VERSION_1_1)


@blueprint.route('')
@produces('text/csv', response_content_type='text/csv; charset=utf8')
@auth.login_required
@exception_catcher
def list():
    if 'start_date' in request.args or 'end_date' in request.args:
        return _list_period()
    else:
        return _list_all()


def _list_all():
    call_logs = services.find_all()
    return _list_call_logs(call_logs)


def _list_period():
    start, end = _extract_datetimes(request.args)
    call_logs = services.find_all_in_period(start, end)
    return _list_call_logs(call_logs)


def _extract_datetimes(request_args):
    invalid_parameters = []
    start = _extract_datetime('start_date', request_args, invalid_parameters)
    end = _extract_datetime('end_date', request_args, invalid_parameters)
    if invalid_parameters:
        raise InvalidParametersError(invalid_parameters)
    return start, end


def _extract_datetime(datetime_key, request_args, invalid_parameters):
    if datetime_key in request_args:
        try:
            return _decode_datetime(request_args[datetime_key])
        except ValueError:
            invalid_parameters.append(datetime_key)
    else:
        return None


def _list_call_logs(call_logs):
    mapped_call_logs = map(mapper.to_api, call_logs)
    response = serializer.encode_list(mapped_call_logs)
    return make_response(response, 200, {'Content-disposition': 'attachment;filename=xivo-call-logs.csv'})


def _decode_datetime(datetime_str):
    result = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S')
    return result
