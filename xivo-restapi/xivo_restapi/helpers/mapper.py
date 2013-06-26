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


class AbstractMapper(object):

    @classmethod
    def run_one_object(cls, object_dao):
        res = {}
        for obj_attr, mapping_key in cls._MAPPING.iteritems():
            if hasattr(object_dao, obj_attr):
                res[mapping_key] = getattr(object_dao, obj_attr)
        return res

    @classmethod
    def run_list_object(cls, object_list):
        res = []
        for object_dao in object_list:
            res.append(cls.run_one_object(object_dao))
        return res
