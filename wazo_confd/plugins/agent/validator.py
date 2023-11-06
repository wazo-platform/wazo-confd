# Copyright 2018-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.agent import dao as agent_dao

from wazo_confd.helpers.validator import (
    Optional,
    UniqueField,
    UniqueFieldChanged,
    ValidationGroup,
)


def build_validator():
    return ValidationGroup(
        create=[
            UniqueField(
                'number',
                lambda number, tenant_uuids: agent_dao.find_by(
                    number=number, tenant_uuids=tenant_uuids
                ),
                'Agent',
            )
        ],
        edit=[
            Optional('number', UniqueFieldChanged('number', agent_dao.find_by, 'Agent'))
        ],
    )
