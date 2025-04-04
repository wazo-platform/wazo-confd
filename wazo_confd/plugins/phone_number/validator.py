# Copyright 2024-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.phone_number import dao

from wazo_confd.helpers.validator import (
    UniqueInTenantValidator,
    ValidationGroup,
    Validator,
)


class OnlyOneMainByTenantValidator(Validator):
    def __init__(self, dao):
        self.dao = dao

    def validate(self, phone_number):
        if not phone_number.main:
            return

        existing = self.dao.find_by(main=True, tenant_uuid=phone_number.tenant_uuid)
        if existing and existing.uuid != phone_number.uuid:
            raise errors.resource_exists(
                'PhoneNumber',
                main=True,
                tenant_uuid=str(phone_number.tenant_uuid),
            )


def build_validator():
    return ValidationGroup(
        create=[
            OnlyOneMainByTenantValidator(dao),
            UniqueInTenantValidator('number', dao, 'PhoneNumber', update=False),
        ],
        edit=[
            OnlyOneMainByTenantValidator(dao),
            UniqueInTenantValidator('number', dao, 'PhoneNumber', update=True),
        ],
    )
