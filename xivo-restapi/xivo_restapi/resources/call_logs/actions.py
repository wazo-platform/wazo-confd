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
from flask import Blueprint
from flask.helpers import make_response
from xivo_dao.data_handler.call_log import services
from xivo_restapi import config
from xivo_restapi.authentication.xivo_realm_digest import realmDigest
from xivo_restapi.helpers.common import exception_catcher
from xivo_restapi.negotiate.flask_negotiate import produces
from xivo_restapi.resources.call_logs import serializer
from xivo_restapi.resources.call_logs import mapper

logger = logging.getLogger(__name__)
blueprint = Blueprint('call_logs', __name__, url_prefix='/%s/call_logs' % config.VERSION_1_1)


@blueprint.route('')
@realmDigest.requires_auth
@produces('text/csv', response_content_type='text/csv; charset=utf8')
@exception_catcher
def list():
    call_logs = services.find_all()
    mapped_call_logs = map(mapper.to_api, call_logs)
    response = serializer.encode_list(mapped_call_logs)
    return make_response(response, 200, {'Content-disposition': 'attachment;filename=xivo-call-logs.csv'})
