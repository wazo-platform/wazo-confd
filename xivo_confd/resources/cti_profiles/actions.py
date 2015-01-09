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
from flask.helpers import make_response
from flask_negotiate import produces

from xivo_confd import config
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Unicode, Int
from xivo_dao.data_handler.cti_profile import services
from xivo_dao.data_handler.cti_profile.model import CtiProfile


def load(core_rest_api):
    blueprint = Blueprint('cti_profiles', __name__, url_prefix='/%s/cti_profiles' % config.API_VERSION)
    document = core_rest_api.content_parser.document(
        Field('id', Int()),
        Field('name', Unicode())
    )
    converter = Converter.for_resource(document, CtiProfile, 'cti_profiles')

    @blueprint.route('', methods=['GET'])
    @core_rest_api.auth.login_required
    @produces('application/json')
    def find_all():
        profiles = services.find_all()
        items = converter.encode_list(profiles)
        return make_response(items, 200)

    @blueprint.route('/<int:resource_id>', methods=['GET'])
    @core_rest_api.auth.login_required
    @produces('application/json')
    def get(resource_id):
        profile = services.get(resource_id)
        result = converter.encode(profile)
        return make_response(result, 200)

    core_rest_api.register(blueprint)
