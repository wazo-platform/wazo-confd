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

from datetime import datetime

from flask import Blueprint
from flask import Response
from flask import request
from xivo_dao.helpers import errors

from xivo_confd import config
from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.resources.call_logs import mapper
from xivo_confd.resources.call_logs import serializer
from xivo_confd.resources.call_logs import services


def load(core_rest_api):
    blueprint = Blueprint('call_logs', __name__, url_prefix='/%s/call_logs' % config.API_VERSION)

    @blueprint.route('')
    @core_rest_api.auth.login_required
    @required_acl('confd.call_logs.read')
    def get_call_logs():
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
        start = _extract_datetime('start_date', request_args)
        end = _extract_datetime('end_date', request_args)
        return start, end

    def _extract_datetime(datetime_key, request_args):
        if datetime_key in request_args:
            try:
                return _decode_datetime(request_args[datetime_key])
            except ValueError:
                raise errors.wrong_type(datetime_key, 'datetime')
        raise errors.missing(datetime_key)

    def _list_call_logs(call_logs):
        mapped_call_logs = map(mapper.to_api, call_logs)
        response = serializer.encode_list(mapped_call_logs)
        return Response(response=response,
                        status=200,
                        headers={'Content-disposition': 'attachment;filename=xivo-call-logs.csv'},
                        content_type='text/csv; charset=utf-8')

    def _decode_datetime(datetime_str):
        result = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S')
        return result

    core_rest_api.register(blueprint)
