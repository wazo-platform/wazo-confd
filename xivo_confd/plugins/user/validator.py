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

from xivo_confd.helpers.validator import (MemberOfSequence,
                                          NumberRange,
                                          Optional,
                                          RegexField,
                                          RequiredFields,
                                          ResourceExists,
                                          UniqueField,
                                          UniqueFieldChanged,
                                          ValidationGroup,
                                          Validator)

from xivo_dao.helpers import errors
from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_dao.resources.user_voicemail import dao as user_voicemail_dao
from xivo_dao.resources.language import dao as language_dao

from xivo_confd.database import entity as entity_db


MOBILE_PHONE_NUMBER_REGEX = r"^\+?[0-9\*#]+$"
CALLER_ID_REGEX = r'^"(.*)"( <\+?\d+>)?$'
USERNAME_PASSWORD_REGEX = r"^[a-zA-Z0-9-\._~\!\$&\'\(\)\*\+,;=%]+$"
CALL_PERMISSION_PASSWORD_REGEX = r"^[0-9#\*]{1,40}"


class NoVoicemailAssociated(Validator):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, user):
        user_voicemail = self.dao.find_by_user_id(user.id)
        if user_voicemail:
            raise errors.resource_associated('User',
                                             'Voicemail',
                                             user_id=user_voicemail.user_id,
                                             voicemail_id=user_voicemail.voicemail_id)


class NoLineAssociated(Validator):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, user):
        user_lines = self.dao.find_all_by_user_id(user.id)
        if user_lines:
            ids = tuple(ul.line_id for ul in user_lines)
            raise errors.resource_associated('User', 'Line', line_ids=ids)


class NoEmptyFieldWhenEnabled(Validator):

    def __init__(self, field, enabled):
        self.field = field
        self.enabled = enabled

    def validate(self, model):
        if getattr(model, self.enabled):
            if getattr(model, self.field) is None:
                raise errors.forward_destination_null()


def build_validator():
    return ValidationGroup(
        common=[
            RequiredFields('firstname'),
            Optional('mobile_phone_number',
                     RegexField.compile('mobile_phone_number', MOBILE_PHONE_NUMBER_REGEX)),
            Optional('caller_id',
                     RegexField.compile('caller_id', CALLER_ID_REGEX)),
            Optional('username',
                     RegexField.compile('username', USERNAME_PASSWORD_REGEX)),
            Optional('password',
                     RegexField.compile('password', USERNAME_PASSWORD_REGEX)),
            Optional('call_permission_password',
                     RegexField.compile('call_permission_password', CALL_PERMISSION_PASSWORD_REGEX)),
            Optional('ring_seconds',
                     NumberRange('ring_seconds', minimum=0, maximum=60, step=5)),
            Optional('simultaneous_calls',
                     NumberRange('simultaneous_calls', minimum=1, maximum=20)),
            Optional('language',
                     MemberOfSequence('language', language_dao.find_all)),
            Optional('entity_id',
                     ResourceExists('entity_id',
                                    entity_db.entity_id_exists,
                                    'Entity'))
        ],
        delete=[
            NoVoicemailAssociated(user_voicemail_dao),
            NoLineAssociated(user_line_dao)
        ],
        create=[
            Optional('email',
                     UniqueField('email',
                                 lambda email: user_dao.find_by(email=email),
                                 'User'))
        ],
        edit=[
            RequiredFields('call_transfer_enabled',
                           'call_record_enabled',
                           'online_call_record_enabled',
                           'supervision_enabled',
                           'ring_seconds',
                           'simultaneous_calls',
                           'caller_id'),
            Optional('email',
                     UniqueFieldChanged('email', user_dao, 'User')),
        ]
    )


def build_validator_forward():
    return ValidationGroup(
        edit=[
            Optional('busy_enabled',
                     NoEmptyFieldWhenEnabled('busy_destination', 'busy_enabled')),
            Optional('noanswer_enabled',
                     NoEmptyFieldWhenEnabled('noanswer_destination', 'noanswer_enabled')),
            Optional('unconditional_enabled',
                     NoEmptyFieldWhenEnabled('unconditional_destination', 'unconditional_enabled'))
        ]
    )
