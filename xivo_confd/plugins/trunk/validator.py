# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.helpers.validator import ValidationGroup, GetResource, Optional
from xivo_dao.resources.context import dao as context_dao


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
