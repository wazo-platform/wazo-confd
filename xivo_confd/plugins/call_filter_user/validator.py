# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class CallFilterRecipientUserAssociationValidator(ValidatorAssociation):

    def validate(self, call_filter, users):
        self.validate_no_more_than_one_user(users)

    def validate_no_more_than_one_user(self, users):
        if len(users) > 1:
            raise errors.not_permitted('Cannot associate more than one recipient')


class CallFilterSurrogateUserAssociationValidator(ValidatorAssociation):

    def validate(self, call_filter, users):
        self.validate_no_duplicate_user(users)

    def validate_no_duplicate_user(self, users):
        if len(users) != len(set(users)):
            raise errors.not_permitted('Cannot associate same user more than once')


def build_validator_recipient_user():
    return ValidationAssociation(
        association=[CallFilterRecipientUserAssociationValidator()],
    )


def build_validator_surrogate_user():
    return ValidationAssociation(
        association=[CallFilterSurrogateUserAssociationValidator()],
    )
