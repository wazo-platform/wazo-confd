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


class AbstractMapper(object):

    @classmethod
    def map(cls, data, **kwargs):
        if isinstance(data, list):
            result = cls._map_objects(data, **kwargs)
        else:
            result = cls._map_object(data, **kwargs)
        return result

    @classmethod
    def encode(cls, data, **kwargs):
        result = cls.map(data, **kwargs)
        return serializer.encode(result)

    @classmethod
    def _map_object(cls, object_dao, **kwargs):
        res = {}
        for obj_attr, mapping_key in cls._MAPPING.iteritems():
            if hasattr(object_dao, obj_attr):
                res[mapping_key] = getattr(object_dao, obj_attr)
        return res

    @classmethod
    def _map_objects(cls, object_list, **kwargs):
        res = []
        for object_dao in object_list:
            res.append(cls._map_object(object_dao, **kwargs))
        return cls._process_paginated_data(res)

    @classmethod
    def _process_paginated_data(cls, items):
        result = {
            'total': len(items),
            'items': items
        }
        return result
