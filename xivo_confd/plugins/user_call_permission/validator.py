# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation

from xivo_dao.helpers import errors
from xivo_dao.resources.user_call_permission import dao as user_call_permission_dao


class UserCallPermissionAssociationValidator(ValidatorAssociation):

    def validate(self, user, call_permission):
        self.validate_user_not_already_associated(user, call_permission)

    def validate_user_not_already_associated(self, user, call_permission):
        user_call_permission = user_call_permission_dao.find_by(user_id=user.id,
                                                                call_permission_id=call_permission.id)
        if user_call_permission:
            raise errors.resource_associated('User', 'CallPermission',
                                             user_id=user.id, call_permission_id=call_permission.id)


def build_validator():
    return ValidationAssociation(
        association=[
            UserCallPermissionAssociationValidator()
        ]
    )
