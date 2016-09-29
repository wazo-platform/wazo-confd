# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_confd.helpers.validator import (FindResource,
                                          UniqueField,
                                          UniqueFieldChanged,
                                          Validator,
                                          ValidationGroup)

from xivo_dao.helpers import errors
from xivo_dao.resources.context import dao as context_dao
from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.outcall import dao as outcall_dao


class PatternsValidator(Validator):

    def __init__(self, extension_dao):
        self.extension_dao = extension_dao

    def validate(self, outcall):
        for pattern in outcall.patterns:
            self.validate_pattern(outcall.context, pattern)

    def validate_pattern(self, context, pattern):
        extension = self.extension_dao.find_by(exten=pattern.pattern,
                                               context=context)
        if extension and extension != pattern.extension:
            raise errors.resource_exists('Extension',
                                         exten=extension.exten,
                                         context=extension.context)


def build_validator():
    common_validators = [
            FindResource('context', context_dao.find, 'Context'),
            PatternsValidator(extension_dao),
    ]
    return ValidationGroup(
        create=[
            UniqueField('name',
                        lambda name: outcall_dao.find_by(name=name),
                        'Outcall'),
        ] + common_validators,
        edit=[
            UniqueFieldChanged('name', outcall_dao, 'Outcall'),
        ] + common_validators
    )
