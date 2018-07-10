# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.skill import dao as skill_dao

from xivo_confd.helpers.validator import (
    UniqueField,
    UniqueFieldChanged,
    ValidationGroup,
)


def build_validator():
    return ValidationGroup(
        create=[
            UniqueField('name',
                        lambda name: skill_dao.find_by(name=name),
                        'Skill'),
        ],
        edit=[
            UniqueFieldChanged('name', skill_dao, 'Skill'),
        ]
    )
