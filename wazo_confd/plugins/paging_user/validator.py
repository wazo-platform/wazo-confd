# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors

from wazo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class PagingUserAssociationValidator(ValidatorAssociation):
    def validate(self, paging, users):
        for user in users:
            self.validate_same_tenant(paging, user)
        self.validate_no_duplicate_user(users)

    def validate_same_tenant(self, paging, user):
        if paging.tenant_uuid != user.tenant_uuid:
            raise errors.different_tenants(
                paging_tenant_uuid=paging.tenant_uuid, user_tenant_uuid=user.tenant_uuid
            )

    def validate_no_duplicate_user(self, users):
        if len(users) != len(set(users)):
            raise errors.not_permitted('Cannot associate same user more than once')


def build_validator():
    return ValidationAssociation(association=[PagingUserAssociationValidator()])
