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


from flask import Blueprint
from flask import Response
from flask import request
from flask import url_for
from flask_negotiate import consumes
from flask_negotiate import produces
from xivo_dao.data_handler.voicemail import services as voicemail_services
from xivo_dao.data_handler.voicemail.model import Voicemail

from xivo_confd import config
from xivo_confd.helpers.common import extract_search_parameters
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Unicode, Int, Boolean


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
    @produces('application/json')
    def get_voicemails():
        search_parameters = extract_search_parameters(request.args)
        search_result = voicemail_services.search(**search_parameters)
        response = converter.encode_list(search_result.items, search_result.total)
        return Response(response=response,
                        status=200,
                        content_type='application/json')

    @blueprint.route('/<int:resource_id>')
    @core_rest_api.auth.login_required
    @produces('application/json')
    def get(resource_id):
        voicemail = voicemail_services.get(resource_id)
        response = converter.encode(voicemail)
        return Response(response=response,
                        status=200,
                        content_type='application/json')

    @blueprint.route('', methods=['POST'])
    @core_rest_api.auth.login_required
    @produces('application/json')
    @consumes('application/json')
    def create():
        voicemail = converter.decode(request)
        created_voicemail = voicemail_services.create(voicemail)
        response = converter.encode(created_voicemail)
        location = url_for('.get', resource_id=created_voicemail.id)
        return Response(response=response,
                        status=201,
                        content_type='application/json',
                        headers={'Location': location})

    @blueprint.route('/<int:resource_id>', methods=['PUT'])
    @core_rest_api.auth.login_required
    @consumes('application/json')
    def edit(resource_id):
        voicemail = voicemail_services.get(resource_id)
        converter.update(request, voicemail)
        voicemail_services.edit(voicemail)
        return Response(status=204)

    @blueprint.route('/<int:resource_id>', methods=['DELETE'])
    @core_rest_api.auth.login_required
    def delete(resource_id):
        voicemail = voicemail_services.get(resource_id)
        voicemail_services.delete(voicemail)
        return Response(status=204)

    core_rest_api.register(blueprint)
