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

from flask import Response
from flask import request
from flask import url_for
from flask_negotiate import consumes
from flask_negotiate import produces
from xivo_dao.data_handler.user_voicemail import services as user_voicemail_services
from xivo_dao.data_handler.user_voicemail.model import UserVoicemail

from xivo_confd.helpers import url
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Int, Boolean


def load(core_rest_api):
    user_blueprint = core_rest_api.blueprint('users')
    document = core_rest_api.content_parser.document(
        Field('user_id', Int()),
        Field('voicemail_id', Int()),
        Field('enabled', Boolean())
    )
    converter = Converter.for_request(document, UserVoicemail, {'users': 'user_id',
                                                                'voicemails': 'voicemail_id'})

    @user_blueprint.route('/<int:user_id>/voicemail', methods=['POST'])
    @core_rest_api.auth.login_required
    @produces('application/json')
    @consumes('application/json')
    def associate_voicemail(user_id):
        url.check_user_exists(user_id)
        model = converter.decode(request)
        created_model = user_voicemail_services.associate(model)
        response = converter.encode(created_model)
        location = url_for('.associate_voicemail', user_id=user_id)
        return Response(response=response,
                        status=201,
                        content_type='application/json',
                        headers={'Location': location})

    @user_blueprint.route('/<int:user_id>/voicemail')
    @core_rest_api.auth.login_required
    @produces('application/json')
    def get_user_voicemail(user_id):
        url.check_user_exists(user_id)
        user_voicemail = user_voicemail_services.get_by_user_id(user_id)
        response = converter.encode(user_voicemail)
        return Response(response=response,
                        status=200,
                        content_type='application/json')

    @user_blueprint.route('/<int:user_id>/voicemail', methods=['DELETE'])
    @core_rest_api.auth.login_required
    def dissociate_voicemail(user_id):
        url.check_user_exists(user_id)
        user_voicemail = user_voicemail_services.get_by_user_id(user_id)
        user_voicemail_services.dissociate(user_voicemail)
        return Response(status=204)

    core_rest_api.register(user_blueprint)
