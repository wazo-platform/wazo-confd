# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation

from xivo_dao.helpers import errors


class OutcallCallPermissionAssociationValidator(ValidatorAssociation):

    def validate(self, outcall, call_permission):
        self.validate_outcall_not_already_associated(outcall, call_permission)

    def validate_outcall_not_already_associated(self, outcall, call_permission):
        if call_permission in outcall.call_permissions:
            raise errors.resource_associated('Outcall', 'CallPermission',
                                             outcall_id=outcall.id,
                                             call_permission_id=call_permission.id)


def build_validator():
    return ValidationAssociation(
        association=[
            OutcallCallPermissionAssociationValidator()
        ]
    )
