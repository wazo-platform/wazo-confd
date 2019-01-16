# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.outcall import dao as outcall_dao

from xivo_confd.helpers.validator import (
    UniqueField,
    UniqueFieldChanged,
    ValidationGroup,
)


def build_validator():
    return ValidationGroup(
        create=[
            UniqueField('name',
                        lambda name: outcall_dao.find_by(name=name),
                        'Outcall'),
        ],
        edit=[
            UniqueFieldChanged('name', outcall_dao, 'Outcall'),
        ]
    )
