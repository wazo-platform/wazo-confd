# -*- coding: UTF-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors
from xivo_dao.resources.context import dao as context_dao
from xivo_dao.resources.line import dao as line_dao

from xivo_confd.helpers.validator import (
    GetResource,
    MemberOfSequence,
    Optional,
    ValidationGroup,
    Validator,
)


class ProvCodeAvailable(Validator):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, line):
        existing = self.dao.find_by(provisioningid=line.provisioningid)
        if existing:
            raise errors.resource_exists('Line', provisioning_code=line.provisioning_code)


class ProvCodeChanged(ProvCodeAvailable):

    def validate(self, line):
        old_line = self.dao.get(line.id)
        if old_line.provisioning_code != line.provisioning_code:
            super(ProvCodeChanged, self).validate(line)


def build_validator(device_dao):
    return ValidationGroup(
        create=[
            Optional(
                'provisioning_code',
                ProvCodeAvailable(line_dao)
            ),
            Optional(
                'registrar',
                MemberOfSequence('registrar', device_dao.registrars, 'Registrar')
            ),
            GetResource('context', context_dao.get_by_name, 'Context'),
        ],
        edit=[
            ProvCodeChanged(line_dao),
            MemberOfSequence('registrar', device_dao.registrars, 'Registrar'),
            GetResource('context', context_dao.get_by_name, 'Context'),
        ])
