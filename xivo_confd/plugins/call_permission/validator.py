# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.helpers.validator import (Optional,
                                          UniqueField,
                                          UniqueFieldChanged,
                                          ValidationGroup)
from xivo_dao.resources.call_permission import dao as call_permission_dao


def build_validator():
    return ValidationGroup(
        create=[
            UniqueField('name',
                        lambda name: call_permission_dao.find_by(name=name),
                        'CallPermission')
        ],
        edit=[
            Optional('name',
                     UniqueFieldChanged('name', call_permission_dao, 'CallPermission'))
        ]
    )
