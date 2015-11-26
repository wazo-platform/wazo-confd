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

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.voicemail import dao as voicemail_dao
from xivo_dao.resources.user_voicemail import dao as user_voicemail_dao

from xivo_dao.resources.user_voicemail.model import UserVoicemail

from xivo_confd.helpers.converter import Converter, LinkGenerator
from xivo_confd.helpers.mooltiparse import Field, Int, Boolean
from xivo_confd.helpers.resource import DecoratorChain

from xivo_confd.resources.user_voicemail.services import UserVoicemailService
from xivo_confd.resources.user_voicemail.resource import UserVoicemailResource
from xivo_confd.resources.user_voicemail.validator import build_validator
from xivo_confd.resources.user_voicemail import notifier


def load(core_rest_api):
    user_blueprint = core_rest_api.blueprint('users')
    vm_blueprint = core_rest_api.blueprint('voicemails')

    document = core_rest_api.content_parser.document(
        Field('user_id', Int()),
        Field('voicemail_id', Int()),
        Field('enabled', Boolean())
    )

    links = [LinkGenerator('users', route='users', id_name='id', field_name='user_id'),
             LinkGenerator('voicemails', id_name='resource_id', field_name='voicemail_id')]

    converter = Converter.association(document, UserVoicemail,
                                      links=links,
                                      rename={'parent_id': 'user_id'})
    validator = build_validator()

    service = UserVoicemailService(user_dao,
                                   voicemail_dao,
                                   user_voicemail_dao,
                                   validator,
                                   notifier)
    resource = UserVoicemailResource(service, converter)

    user_chain = DecoratorChain(core_rest_api, user_blueprint)
    vm_chain = DecoratorChain(core_rest_api, vm_blueprint)

    (user_chain
     .get('/<int:parent_id>/voicemail')
     .decorate(resource.get_association))

    (user_chain
     .create('/<int:parent_id>/voicemail')
     .decorate(resource.associate))

    (user_chain
     .delete('/<int:parent_id>/voicemail')
     .decorate(resource.dissociate))

    (vm_chain
     .get('/<int:voicemail_id>/users')
     .decorate(resource.list_associations_by_child))

    core_rest_api.register(user_blueprint)
    core_rest_api.register(vm_blueprint)
