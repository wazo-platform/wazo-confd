# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.user_line import dao as user_line_dao

from xivo_confd.helpers.validator import (
    Optional,
    UniqueField,
    UniqueFieldChanged,
    ValidationGroup,
    Validator,
)


class NoVoicemailAssociated(Validator):

    def validate(self, user):
        if user.voicemail:
            raise errors.resource_associated('User',
                                             'Voicemail',
                                             user_id=user.id,
                                             voicemail_id=user.voicemail.id)


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
        delete=[
            NoVoicemailAssociated(),
            NoLineAssociated(user_line_dao)
        ],
        create=[
            Optional('email',
                     UniqueField('email',
                                 lambda email: user_dao.find_by(email=email),
                                 'User')),
            Optional('username',
                     UniqueField('username',
                                 lambda username: user_dao.find_by(username=username),
                                 'User'))
        ],
        edit=[
            Optional('email',
                     UniqueFieldChanged('email', user_dao, 'User')),
            Optional('username',
                     UniqueFieldChanged('username', user_dao, 'User')),
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
