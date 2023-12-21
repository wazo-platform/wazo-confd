# Copyright 2018-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.agent import dao as agent_dao

from wazo_confd.helpers.validator import UniqueField, ValidationGroup, Validator


class NumberChanged(Validator):
    def validate(self, model):
        agent_dao.find_by(number=model.number, tenant_uuids=[model.tenant_uuid])


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
        edit=[NumberChanged()],
    )
