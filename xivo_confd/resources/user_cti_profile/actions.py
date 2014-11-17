# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from flask import request
from flask.helpers import make_response

from xivo_confd.resources.users.routes import route

from xivo_dao.data_handler.user_cti_profile import services as user_cti_profile_services
from xivo_dao.data_handler.user_cti_profile.model import UserCtiProfile

from xivo_confd.helpers import url
from xivo_confd.flask_http_server import content_parser
from xivo_confd.helpers.mooltiparse import Field, Int, Boolean
from xivo_confd.helpers.converter import Converter


document = content_parser.document(
    Field('user_id', Int()),
    Field('cti_profile_id', Int()),
    Field('enabled', Boolean())
)

converter = Converter.for_request(document, UserCtiProfile, {'users': 'user_id',
                                                             'cti_profiles': 'cti_profile_id'})


@route('/<int:user_id>/cti', methods=['PUT'])
def edit_cti_configuration(user_id):
    url.check_user_exists(user_id)
    user_cti_profile = converter.decode(request)
    user_cti_profile_services.edit(user_cti_profile)
    return make_response('', 204)


@route('/<int:user_id>/cti', methods=['GET'])
def get_cti_configuration(user_id):
    url.check_user_exists(user_id)
    user_cti_profile = user_cti_profile_services.get(user_id)
    encoded_profile = converter.encode(user_cti_profile)
    return make_response(encoded_profile, 200)
