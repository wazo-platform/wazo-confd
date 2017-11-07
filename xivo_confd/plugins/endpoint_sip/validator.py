# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.helpers.validator import (ValidationGroup,
                                          Optional,
                                          UniqueField,
                                          UniqueFieldChanged)
from xivo_dao.resources.endpoint_sip import dao as sip_dao


def build_validator():
    return ValidationGroup(
        create=[
            Optional('name',
                     UniqueField('name',
                                 lambda v: sip_dao.find_by(name=v),
                                 'SIPEndpoint'),
                     ),
        ],
        edit=[
            Optional('name',
                     UniqueFieldChanged('name', sip_dao, 'SIPEndpoint'))
        ])
