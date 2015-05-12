# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-2015 Avencall
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

from xivo_dao.data_handler.user_voicemail import services as user_voicemail_services
from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.voicemail import dao as voicemail_dao
from xivo_dao.resources.user_voicemail.model import UserVoicemail

from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Int, Boolean

from xivo_confd.helpers.resource import DecoratorChain, SingleAssociationResource


class UserVoicemailService(object):

    def __init__(self, service, user_dao, voicemail_dao):
        self.service = service
        self.user_dao = user_dao
        self.voicemail_dao = voicemail_dao

    def validate_parent(self, user_id):
        self.user_dao.get(user_id)

    def validate_resource(self, voicemail_id):
        self.voicemail_dao.get(voicemail_id)

    def get_by_parent(self, user_id):
        return self.service.get_by_user_id(user_id)

    def associate(self, association):
        return self.service.associate(association)

    def dissociate(self, association):
        self.service.dissociate(association)


def load(core_rest_api):
    user_blueprint = core_rest_api.blueprint('users')
    document = core_rest_api.content_parser.document(
        Field('user_id', Int()),
        Field('voicemail_id', Int()),
        Field('enabled', Boolean())
    )
    converter = Converter.association(document, UserVoicemail,
                                      links={'users': 'user_id',
                                             'voicemails': 'voicemail_id'},
                                      rename={'parent_id': 'user_id'})

    service = UserVoicemailService(user_voicemail_services, user_dao, voicemail_dao)
    resource = SingleAssociationResource(service, converter)

    chain = DecoratorChain(core_rest_api, user_blueprint)

    (chain
     .get('/<int:parent_id>/voicemail')
     .decorate(resource.get_association))

    (chain
     .create('/<int:parent_id>/voicemail')
     .decorate(resource.associate))

    (chain
     .delete('/<int:parent_id>/voicemail')
     .decorate(resource.dissociate))

    core_rest_api.register(user_blueprint)
