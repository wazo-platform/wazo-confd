# Copyright 2013-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.moh import dao as moh_dao
from xivo_dao.resources.user import dao as user_dao

from wazo_confd.helpers.validator import (
    MOHExists,
    Optional,
    UniqueField,
    UniqueFieldChanged,
    ValidationGroup,
    Validator,
)


class NoVoicemailAssociated(Validator):
    def validate(self, user):
        if user.voicemail:
            raise errors.resource_associated(
                'User', 'Voicemail', user_id=user.id, voicemail_id=user.voicemail.id
            )


class NoEmptyFieldWhenEnabled(Validator):
    def __init__(self, field, enabled, error_func=None):
        self.field = field
        self.enabled = enabled
        self._error_func = error_func or errors.forward_destination_null

    def validate(self, model):
        if getattr(model, self.enabled):
            if getattr(model, self.field) is None:
                raise self._error_func()


class NonGlobalVoicemailAssigned(Validator):
    def validate(self, model):
        if model.voicemail and model.voicemail.accesstype == 'global':
            raise errors.not_permitted(
                'A global voicemail cannot be associated to users.'
            )


def build_validator():
    moh_validator = MOHExists('music_on_hold', moh_dao.get_by)
    pstn_fallback_validator = NoEmptyFieldWhenEnabled(
        'mobile_phone_number',
        'mobile_fallback_enabled',
        error_func=errors.mobile_fallback_number_null,
    )
    return ValidationGroup(
        delete=[NoVoicemailAssociated()],
        create=[
            Optional(
                'email',
                UniqueField(
                    'email', lambda email: user_dao.find_by(email=email), 'User'
                ),
            ),
            Optional(
                'username',
                UniqueField(
                    'username',
                    lambda username: user_dao.find_by(username=username),
                    'User',
                ),
            ),
            moh_validator,
            NonGlobalVoicemailAssigned(),
            Optional('mobile_fallback_enabled', pstn_fallback_validator),
        ],
        edit=[
            Optional('email', UniqueFieldChanged('email', user_dao.find_by, 'User')),
            Optional(
                'username', UniqueFieldChanged('username', user_dao.find_by, 'User')
            ),
            moh_validator,
            NonGlobalVoicemailAssigned(),
            Optional('mobile_fallback_enabled', pstn_fallback_validator),
        ],
    )


def build_validator_forward():
    return ValidationGroup(
        edit=[
            Optional(
                'busy_enabled',
                NoEmptyFieldWhenEnabled('busy_destination', 'busy_enabled'),
            ),
            Optional(
                'noanswer_enabled',
                NoEmptyFieldWhenEnabled('noanswer_destination', 'noanswer_enabled'),
            ),
            Optional(
                'unconditional_enabled',
                NoEmptyFieldWhenEnabled(
                    'unconditional_destination', 'unconditional_enabled'
                ),
            ),
        ]
    )
