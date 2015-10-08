# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_confd.helpers.validator import ValidationGroup, FindResource, RequiredFields, Validator, Optional
from xivo_dao.resources.context import dao as context_dao
from xivo_dao.resources.line import dao as line_dao
from xivo_dao.helpers import errors


class ProvCodeAvailable(Validator):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, line):
        existing = self.dao.find_by('provisioningid', (line.provisioningid))
        if existing:
            raise errors.resource_exists('Line', provisioning_code=line.provisioning_code)


class ProvCodeChanged(ProvCodeAvailable):

    def validate(self, line):
        old_line = self.dao.get(line.id)
        if old_line.provisioning_code != line.provisioning_code:
            super(ProvCodeChanged, self).validate(line)


def build_validator():
    return ValidationGroup(
        common=[
            RequiredFields('context'),
            FindResource('context', context_dao.find, 'Context')
        ],
        create=[
            Optional('provisioning_code', ProvCodeAvailable(line_dao))
        ],
        edit=[
            ProvCodeChanged(line_dao),
            RequiredFields('provisioning_code', 'position')
        ])
