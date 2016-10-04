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

from xivo_confd.helpers.validator import (UniqueField,
                                          UniqueFieldChanged,
                                          ValidationGroup)

from xivo_dao.resources.outcall import dao as outcall_dao


def build_validator():
    return ValidationGroup(
        create=[
            UniqueField('name',
                        lambda name: outcall_dao.find_by(name=name),
                        'Outcall'),
        ],
        edit=[
            UniqueFieldChanged('name', outcall_dao, 'Outcall'),
        ]
    )
