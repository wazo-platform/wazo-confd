# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.endpoint_iax import dao as iax_dao

from xivo_confd.helpers.validator import (
    Optional,
    UniqueField,
    UniqueFieldChanged,
    ValidationGroup,
)


def build_validator():
    return ValidationGroup(
        create=[
            Optional('name',
                     UniqueField('name',
                                 lambda value: iax_dao.find_by(name=value),
                                 'IAXEndpoint')),
        ],
        edit=[
            Optional('name',
                     UniqueFieldChanged('name', iax_dao, 'IAXEndpoint'))
        ])
