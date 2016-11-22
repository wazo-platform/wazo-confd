# -*- coding: UTF-8 -*-

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

from marshmallow import post_load

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_confd.helpers.mallow import BaseSchema
from xivo_confd.helpers.destination import DestinationField


class GroupFallbackSchema(BaseSchema):
    noanswer_destination = DestinationField(attribute='noanswer', default=None, allow_none=True)

    @post_load
    def create_objects(self, data):
        for key, form in data.iteritems():
            if form:
                data[key] = Dialaction(**form)
        return data
