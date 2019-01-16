# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class CallPickupGroupValidator(ValidatorAssociation):

    def validate(self, call_pickup, groups):
        self.validate_no_duplicate_group(groups)

    def validate_no_duplicate_group(self, groups):
        if len(groups) != len(set(groups)):
            raise errors.not_permitted('Cannot associate same group more than once')


def build_validator_target_group():
    return ValidationAssociation(
        association=[CallPickupGroupValidator()],
    )


def build_validator_interceptor_group():
    return ValidationAssociation(
        association=[CallPickupGroupValidator()],
    )


class CallPickupUserValidator(ValidatorAssociation):

    def validate(self, call_pickup, users):
        self.validate_no_duplicate_user(users)

    def validate_no_duplicate_user(self, users):
        if len(users) != len(set(users)):
            raise errors.not_permitted('Cannot associate same user more than once')


def build_validator_target_user():
    return ValidationAssociation(
        association=[CallPickupUserValidator()],
    )


def build_validator_interceptor_user():
    return ValidationAssociation(
        association=[CallPickupUserValidator()],
    )
