# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.call_pickup import dao as call_pickup_dao

from xivo_confd.helpers.validator import (
    Optional,
    UniqueField,
    UniqueFieldChanged,
    ValidationGroup,
)


def build_validator():
    return ValidationGroup(
        create=[
            UniqueField(
                'name',
                lambda name: call_pickup_dao.find_by(name=name),
                'CallPickup',
            )
        ],
        edit=[
            Optional(
                'name',
                UniqueFieldChanged('name', call_pickup_dao, 'CallPickup')
            )
        ]
    )
