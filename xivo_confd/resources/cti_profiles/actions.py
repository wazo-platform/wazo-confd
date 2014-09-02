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

from flask.blueprints import Blueprint

from xivo_confd import config
from xivo_confd.helpers.route_generator import RouteGenerator
from xivo_confd.helpers import serializer
from flask.helpers import make_response
from xivo_dao.data_handler.cti_profile import services
from xivo_confd.helpers.formatter import Formatter
from xivo_dao.data_handler.cti_profile.model import CtiProfilexivo_confdfrom . import mapper

blueprint = Blueprint('cti_profiles', __name__, url_prefix='/%s/cti_profiles' % config.VERSION_1_1)
route = RouteGenerator(blueprint)
formatter = Formatter(mapper, serializer, CtiProfile)


@route('', methods=['GET'])
def find_all():
    profiles = services.find_all()
    result = formatter.list_to_api(profiles)
    return make_response(result, 200)


@route('/<int:cti_profile_id>', methods=['GET'])
def get(cti_profile_id):
    profile = services.get(cti_profile_id)
    result = formatter.to_api(profile)
    return make_response(result, 200)
