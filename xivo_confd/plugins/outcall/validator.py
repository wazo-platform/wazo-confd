# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.helpers.validator import (UniqueField,
                                          UniqueFieldChanged,
                                          ValidationGroup)

from xivo_dao.resources.outcall import dao as outcall_dao


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
