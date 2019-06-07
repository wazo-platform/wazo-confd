# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.endpoint_sip import dao as sip_dao

from wazo_confd.helpers.validator import (
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
                                 lambda v: sip_dao.find_by(name=v),
                                 'SIPEndpoint')),
        ],
        edit=[
            Optional('name',
                     UniqueFieldChanged('name', sip_dao, 'SIPEndpoint'))
        ])
