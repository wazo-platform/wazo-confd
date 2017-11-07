# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.helpers.validator import ValidationGroup, UniqueField, UniqueFieldChanged

from xivo_dao.resources.endpoint_custom import dao as custom_dao


def find_by_interface(interface):
    return custom_dao.find_by(interface=interface)


def build_validator():
    return ValidationGroup(
        create=[
            UniqueField('interface', find_by_interface, 'CustomEndpoint')
        ],
        edit=[
            UniqueFieldChanged('interface', custom_dao, 'CustomEndpoint')
        ]
    )
