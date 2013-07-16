# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from xivo_restapi.helpers import serializer


def encode(data):
    return serializer.encode(data)


def encode_list(items):
    return serializer.encode(process_paginated_data(items))


def map_entity(mapping, obj):
    res = {}
    for obj_attr, mapping_key in mapping.iteritems():
        if hasattr(obj, obj_attr):
            res[mapping_key] = getattr(obj, obj_attr)
    return res


def process_paginated_data(items):
    result = {
        'total': len(items),
        'items': items
    }
    return result
