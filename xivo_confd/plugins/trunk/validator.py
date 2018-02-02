# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.context import dao as context_dao

from xivo_confd.helpers.validator import ValidationGroup, GetResource, Optional


def build_validator():
    return ValidationGroup(
        create=[
            Optional('context',
                     GetResource('context', context_dao.get_by_name, 'Context')),
        ],
        edit=[
            Optional('context',
                     GetResource('context', context_dao.get_by_name, 'Context')),
        ]
    )
