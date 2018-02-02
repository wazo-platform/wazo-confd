# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.call_filter import dao as call_filter_dao

from xivo_confd.helpers.validator import (
    Optional,
    UniqueField,
    UniqueFieldChanged,
    ValidationGroup,
)


def build_validator():
    return ValidationGroup(
        create=[
            UniqueField('name',
                        lambda name: call_filter_dao.find_by(name=name),
                        'CallFilter')
        ],
        edit=[
            Optional('name',
                     UniqueFieldChanged('name', call_filter_dao, 'CallFilter'))
        ]
    )
