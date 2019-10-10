# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors

from wazo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class CallFilterRecipientUserAssociationValidator(ValidatorAssociation):
    def validate(self, call_filter, users):
        for user in users:
            self.validate_same_tenant(call_filter, user)
        self.validate_no_more_than_one_user(users)
        self.validate_no_surrogate_user(call_filter, users)

    def validate_same_tenant(self, call_filter, user):
        if call_filter.tenant_uuid != user.tenant_uuid:
            raise errors.different_tenants(
                call_filter_tenant_uuid=call_filter.tenant_uuid,
                user_tenant_uuid=user.tenant_uuid,
            )

    def validate_no_more_than_one_user(self, users):
        if len(users) > 1:
            raise errors.not_permitted('Cannot associate more than one recipient')

    def validate_no_surrogate_user(self, call_filter, users):
        for surrogate in call_filter.surrogates:
            if surrogate.user in users:
                raise errors.resource_associated(
                    'CallFilter',
                    call_filter.id,
                    surrogate_user_uuid=surrogate.user.uuid,
                )


class CallFilterSurrogateUserAssociationValidator(ValidatorAssociation):
    def validate(self, call_filter, users):
        for user in users:
            self.validate_same_tenant(call_filter, user)
        self.validate_no_duplicate_user(users)
        self.validate_no_recipient_user(call_filter, users)

    def validate_same_tenant(self, call_filter, user):
        if call_filter.tenant_uuid != user.tenant_uuid:
            raise errors.different_tenants(
                call_filter_tenant_uuid=call_filter.tenant_uuid,
                user_tenant_uuid=user.tenant_uuid,
            )

    def validate_no_duplicate_user(self, users):
        if len(users) != len(set(users)):
            raise errors.not_permitted('Cannot associate same user more than once')

    def validate_no_recipient_user(self, call_filter, users):
        for recipient in call_filter.recipients:
            if recipient.user in users:
                raise errors.resource_associated(
                    'CallFilter',
                    call_filter.id,
                    recipient_user_uuid=recipient.user.uuid,
                )


def build_validator_recipient_user():
    return ValidationAssociation(
        association=[CallFilterRecipientUserAssociationValidator()]
    )


def build_validator_surrogate_user():
    return ValidationAssociation(
        association=[CallFilterSurrogateUserAssociationValidator()]
    )
