# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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
from flask.globals import request
from flask.helpers import make_response, url_for

from xivo_confd import config
from xivo_confd.helpers.common import extract_search_parameters
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Unicode, Int, Boolean
from xivo_dao.data_handler.voicemail import services as voicemail_services
from xivo_dao.data_handler.voicemail.model import Voicemail


def load(core_rest_api):
    blueprint = Blueprint('voicemails', __name__, url_prefix='/%s/voicemails' % config.API_VERSION)
    document = core_rest_api.content_parser.document(
        Field('id', Int()),
        Field('name', Unicode()),
        Field('number', Unicode()),
        Field('context', Unicode()),
        Field('password', Unicode()),
        Field('email', Unicode()),
        Field('language', Unicode()),
        Field('timezone', Unicode()),
        Field('max_messages', Int()),
        Field('attach_audio', Boolean()),
        Field('delete_messages', Boolean()),
        Field('ask_password', Boolean())
    )
    converter = Converter.for_resource(document, Voicemail)

    @blueprint.route('')
    @core_rest_api.auth.login_required
    def list():
        search_parameters = extract_search_parameters(request.args)
        search_result = voicemail_services.search(**search_parameters)
        encoded_result = converter.encode_list(search_result.items, search_result.total)
        return make_response(encoded_result, 200)

    @blueprint.route('/<int:resource_id>')
    @core_rest_api.auth.login_required
    def get(resource_id):
        voicemail = voicemail_services.get(resource_id)
        encoded_voicemail = converter.encode(voicemail)
        return make_response(encoded_voicemail, 200)

    @blueprint.route('', methods=['POST'])
    @core_rest_api.auth.login_required
    def create():
        voicemail = converter.decode(request)
        created_voicemail = voicemail_services.create(voicemail)
        encoded_voicemail = converter.encode(created_voicemail)
        location = url_for('.get', resource_id=created_voicemail.id)
        return make_response(encoded_voicemail, 201, {'Location': location})

    @blueprint.route('/<int:resource_id>', methods=['PUT'])
    @core_rest_api.auth.login_required
    def edit(resource_id):
        voicemail = voicemail_services.get(resource_id)
        converter.update(request, voicemail)
        voicemail_services.edit(voicemail)
        return make_response('', 204)

    @blueprint.route('/<int:resource_id>', methods=['DELETE'])
    @core_rest_api.auth.login_required
    def delete(resource_id):
        voicemail = voicemail_services.get(resource_id)
        voicemail_services.delete(voicemail)
        return make_response('', 204)

    core_rest_api.register(blueprint)
