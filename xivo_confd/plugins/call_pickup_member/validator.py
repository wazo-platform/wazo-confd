# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class CallPickupUserValidator(ValidatorAssociation):

    def validate(self, call_pickup, users):
        self.validate_no_duplicate_user(users)

    def validate_no_duplicate_user(self, users):
        if len(users) != len(set(users)):
            raise errors.not_permitted('Cannot associate same user more than once')


class CallPickupInterceptorUserAssociationValidator(CallPickupUserValidator):

    def validate(self, call_pickup, users):
        super(CallPickupInterceptorUserAssociationValidator, self).validate(call_pickup, users)
        self.validate_no_interceptor_user(call_pickup, users)

    def validate_no_interceptor_user(self, call_pickup, users):
        for interceptor in call_pickup.interceptors:
            if interceptor.user in users:
                raise errors.resource_associated(
                    'CallPickup',
                    call_pickup.id,
                    interceptor_user_uuid=interceptor.user.uuid,
                )


class CallPickupTargetUserAssociationValidator(CallPickupUserValidator):

    def validate(self, call_pickup, users):
        super(CallPickupTargetUserAssociationValidator, self).validate(call_pickup, users)
        self.validate_no_target_user(call_pickup, users)

    def validate_no_target_user(self, call_pickup, users):
        for target in call_pickup.targets:
            if target.user in users:
                raise errors.resource_associated(
                    'CallPickup',
                    call_pickup.id,
                    target_user_uuid=target.user.uuid,
                )


def build_validator_target_user():
    return ValidationAssociation(
        association=[CallPickupInterceptorUserAssociationValidator()],
    )


def build_validator_interceptor_user():
    return ValidationAssociation(
        association=[CallPickupTargetUserAssociationValidator()],
    )
