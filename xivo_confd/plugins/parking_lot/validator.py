# -*- coding: utf-8 -*-

# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
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

from xivo_dao.helpers import errors
from xivo_dao.resources.extension import dao as extension_dao

from xivo_confd.helpers.validator import ValidationGroup, Validator


class SlotsAvailableValidator(Validator):

    def validate(self, parking_lot):
        if not parking_lot.extensions:
            return

        extensions = extension_dao.find_all_by(context=parking_lot.extensions[0].context)
        for extension in extensions:
            if extension.is_pattern():
                continue
            if parking_lot.in_slots_range(extension.exten):
                raise errors.resource_exists('Extension',
                                             id=extension.id,
                                             exten=extension.exten,
                                             context=extension.context)


def build_validator():
    return ValidationGroup(
        edit=[
            SlotsAvailableValidator(),
        ]
    )
