# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.skill_rule import dao as skill_rule_dao

from xivo_confd.helpers.validator import (
    UniqueField,
    UniqueFieldChanged,
    ValidationGroup,
)


def build_validator():
    return ValidationGroup(
        create=[
            UniqueField('name', lambda name: skill_rule_dao.find_by(name=name), 'SkillRule'),
        ],
        edit=[
            UniqueFieldChanged('name', skill_rule_dao, 'SkillRule'),
        ]
    )
