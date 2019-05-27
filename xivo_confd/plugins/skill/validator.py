# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.skill import dao as skill_dao

from xivo_confd.helpers.validator import (
    UniqueField,
    UniqueFieldChanged,
    ValidationGroup,
)


def build_validator():
    return ValidationGroup(
        create=[
            UniqueField(
                'name',
                lambda name, tenant_uuids: skill_dao.find_by(name=name, tenant_uuids=tenant_uuids),
                'Skill'
            ),
        ],
        edit=[
            UniqueFieldChanged('name', skill_dao, 'Skill'),
        ]
    )
