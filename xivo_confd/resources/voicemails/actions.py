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

from xivo_confd import sysconfd
from xivo_dao.resources.voicemail import dao
from xivo_dao.resources.voicemail.model import Voicemail

from xivo_confd import config
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Unicode, Int, Boolean, Regexp
from xivo_confd.helpers.resource import CRUDResource, DecoratorChain
from xivo_confd.resources.voicemails import notifier
from xivo_confd.resources.voicemails.validator import build_validators
from xivo_confd.resources.voicemails.services import VoicemailService
from xivo_confd.resources.voicemails.mooltiparse import OptionType


def load(core_rest_api):
    blueprint = Blueprint('voicemails', __name__, url_prefix='/%s/voicemails' % config.API_VERSION)
    document = core_rest_api.content_parser.document(
        Field('id', Int()),
        Field('name', Unicode()),
        Field('number',
              Unicode(),
              Regexp.compile(r"\d+", "wrong type. Should be a numeric string")),
        Field('context', Unicode()),
        Field('password',
              Unicode(),
              Regexp.compile(r"\d+", "wrong type. Should be a numeric string")),
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
    validator = build_validators()

    service = VoicemailService(dao, validator, notifier, sysconfd)
    resource = CRUDResource(service, converter)

    DecoratorChain.register_scrud(core_rest_api, blueprint, resource)
