# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.context import dao as context_dao
from xivo_dao.resources.voicemail import dao as voicemail_dao

from wazo_confd.database import static_voicemail
from wazo_confd.helpers.validator import (
    GetResource,
    MemberOfSequence,
    Optional,
    ValidationGroup,
    Validator,
)


class NumberContextExists(Validator):
    def __init__(self, dao):
        self.dao = dao

    def validate(self, model):
        voicemail = self.dao.find_by(number=model.number, context=model.context)
        if voicemail:
            raise errors.resource_exists(
                'Voicemail', number=voicemail.number, context=voicemail.context
            )


class NumberContextChanged(Validator):
    def __init__(self, dao):
        self.dao = dao

    def validate(self, model):
        voicemail = self.dao.find_by(number=model.number, context=model.context)
        if voicemail and voicemail.id != model.id:
            raise errors.resource_exists(
                'Voicemail', number=voicemail.number, context=voicemail.context
            )


class UniqueSharedPerContext(Validator):
    def __init__(self, dao):
        self.dao = dao

    def validate(self, model):
        voicemail = self.dao.find_by(shared=True, context=model.context)
        if voicemail and model.shared and voicemail.id != model.id:
            raise errors.not_permitted(
                'There can be only one shared voicemail per tenant.'
            )


class AssociatedToUser(Validator):
    def validate(self, voicemail):
        if voicemail.users:
            user_ids = ", ".join(str(user.id) for user in voicemail.users)
            raise errors.resource_associated(
                'Voicemail', 'User', voicemail_id=voicemail.id, user_ids=user_ids
            )


class AssociatedToTenant(Validator):
    def validate(self, voicemail):
        if voicemail.shared and len(voicemail.users) > 0:
            raise errors.not_permitted(
                'A shared voicemail cannot be associated to users.'
            )


def build_validator():
    return ValidationGroup(
        common=[
            GetResource('context', context_dao.get_by_name, 'Context'),
            Optional(
                'timezone',
                MemberOfSequence(
                    'timezone', static_voicemail.find_all_timezone, 'Timezone'
                ),
            ),
        ],
        create=[
            NumberContextExists(voicemail_dao),
            UniqueSharedPerContext(voicemail_dao),
            AssociatedToTenant(),
        ],
        edit=[
            NumberContextChanged(voicemail_dao),
            UniqueSharedPerContext(voicemail_dao),
            AssociatedToTenant(),
        ],
        delete=[AssociatedToUser()],
    )
