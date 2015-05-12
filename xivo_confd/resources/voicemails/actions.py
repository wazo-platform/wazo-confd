# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from xivo_confd.helpers import sysconfd_connector
from xivo_dao.resources.voicemail import dao
from xivo_dao.resources.voicemail.model import Voicemail

from xivo_confd import config
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Unicode, Int, Boolean
from xivo_confd.helpers.resource import CRUDResource, CRUDService, DecoratorChain
from xivo_confd.resources.voicemail import validator, notifier


class VoicemailService(CRUDService):

    def __init__(self, dao, validator, notifier, connector, extra=None):
        super(VoicemailService, self).__init__(dao, validator, notifier, extra)
        self.connector = connector

    def delete(self, voicemail):
        super(VoicemailService, self).delete(voicemail)
        self.connector.delete_voicemail_storage(voicemail.number,
                                                voicemail.context)


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
        Field('ask_password', Boolean())
    )
    converter = Converter.resource(document, Voicemail)

    service = VoicemailService(dao, validator, notifier, sysconfd_connector)
    resource = CRUDResource(service, converter)

    DecoratorChain.register_scrud(core_rest_api, blueprint, resource)
