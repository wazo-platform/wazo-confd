# Copyright 2016-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.call_permission import dao as call_permission_dao

from wazo_confd.helpers.validator import (
    UniqueField,
    UniqueFieldChanged,
    ValidationGroup,
)


def build_validator():
    return ValidationGroup(
        create=[
            UniqueField(
                'name',
                lambda name, tenant_uuids: call_permission_dao.find_by(
                    name=name, tenant_uuids=tenant_uuids
                ),
                'CallPermission',
            )
        ],
        edit=[
            UniqueFieldChanged('name', call_permission_dao.find_by, 'CallPermission'),
        ],
    )
