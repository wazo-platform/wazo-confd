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

from functools import partial

from xivo_confd.helpers.validator import ValidationGroup, RequiredFields, Optional, UniqueField
from xivo_dao.resources.endpoint_sip import dao


class UsernameChanged(UniqueField):

    def __init__(self, field, dao_find, dao_get):
        super(UsernameChanged, self).__init__(field, dao_find, 'SIPEndpoint')
        self.dao_get = dao_get

    def validate(self, model):
        existing = self.dao_get(model.id)
        existing_value = getattr(existing, self.field)
        new_value = getattr(model, self.field)
        if existing_value != new_value:
            super(UsernameChanged, self).validate(model)


def build_validator():
    return ValidationGroup(
        create=[
            Optional('name',
                     UniqueField('name',
                                 partial(dao.find_by, 'name')))
        ],
        edit=[
            RequiredFields('name', 'secret', 'type', 'host'),
            UsernameChanged('name',
                            partial(dao.find_by, 'name'),
                            dao.get),
        ])
