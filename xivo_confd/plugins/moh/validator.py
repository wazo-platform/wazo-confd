# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
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
from xivo_dao.resources.moh import dao as moh_dao

from xivo_confd.helpers.validator import (UniqueField,
                                          Validator,
                                          ValidationGroup)


class MohModelValidator(Validator):

    def validate(self, moh):
        if moh.mode == 'custom' and moh.application is None:
            raise errors.moh_custom_no_app()


def build_validator():
    moh_validator = MohModelValidator()

    return ValidationGroup(
        create=[
            UniqueField('name',
                        lambda name: moh_dao.find_by(name=name),
                        'MOH'),
            moh_validator,
        ],
        edit=[
            moh_validator,
        ]
    )
