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


from flask import Blueprint

from xivo_dao.resources.voicemail.model import Voicemail

from xivo_confd import config
from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Unicode, Int, Boolean
from xivo_confd.helpers.resource import CRUDResource, DecoratorChain
from xivo_confd.resources.voicemails.services import build_service
from xivo_confd.resources.voicemails.mooltiparse import OptionType


class VoicemailResource(CRUDResource):

    @required_acl('confd.voicemails.read')
    def search(self):
        return super(VoicemailResource, self).search()

    @required_acl('confd.voicemails.create')
    def create(self):
        return super(VoicemailResource, self).create()

    @required_acl('confd.voicemails.{resource_id}.read')
    def get(self, resource_id):
        return super(VoicemailResource, self).get(resource_id)

    @required_acl('confd.voicemails.{resource_id}.update')
    def edit(self, resource_id):
        return super(VoicemailResource, self).edit(resource_id)

    @required_acl('confd.voicemails.{resource_id}.delete')
    def delete(self, resource_id):
        return super(VoicemailResource, self).delete(resource_id)


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
        Field('pager', Unicode()),
        Field('max_messages', Int()),
        Field('attach_audio', Boolean()),
        Field('delete_messages', Boolean()),
        Field('ask_password', Boolean()),
        Field('enabled', Boolean()),
        Field('options', OptionType())
    )

    converter = Converter.resource(document, Voicemail)

    service = build_service()
    resource = VoicemailResource(service, converter)

    DecoratorChain.register_scrud(core_rest_api, blueprint, resource)
