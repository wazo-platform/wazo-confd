# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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

from xivo_dao.resources.group import dao as group_dao

from xivo_confd.helpers.validator import (Optional,
                                          UniqueField,
                                          UniqueFieldChanged,
                                          ValidationGroup)


def build_validator():
    return ValidationGroup(
        create=[
            UniqueField('name',
                        lambda name: group_dao.find_by(name=name),
                        'Group'),
        ],
        edit=[
            Optional('name',
                     UniqueFieldChanged('name', group_dao, 'Group')),
        ]
    )
