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

from abc import ABCMeta


class AbstractMapping(object):

    __metaclass__ = ABCMeta

    def alchemy_to_sdm(self, alchemy_instance):
        sdm_instance = self.sdm_class()
        return self.map_attributes(alchemy_instance,
                                             sdm_instance,
                                             self.mapping,
                                             self.sdm_types)

    def sdm_to_alchemy(self, sdm_instance):
        alchemy_instance = self.alchemy_class()
        return self.map_attributes(sdm_instance,
                                             alchemy_instance,
                                             self.reverse_mapping,
                                             self.alchemy_types,
                                             self.alchemy_default_values)

    def sdm_to_alchemy_dict(self, user_dict):
        result = {}
        for k in user_dict:
            if k in self.reverse_mapping:
                new_key = self.reverse_mapping[k]
                result[new_key] = user_dict[k]
                if (new_key in self.alchemy_types):
                    result[new_key] = self.alchemy_types[new_key](result[new_key])
            else:
                raise AttributeError()
        return result

    def map_attributes(self, src_object, dst_object, mapping, cast, default_values={}):
        for dst_field in default_values:
            value = default_values[dst_field]
            setattr(dst_object, dst_field, value)
        for src_field in mapping:
            if(hasattr(src_object, src_field)):
                dst_field = mapping[src_field]
                value = getattr(src_object, src_field)
                setattr(dst_object, dst_field, value)
        for dst_field, cast_fct in cast.iteritems():
            value = getattr(dst_object, dst_field)
            if (value is not None):
                setattr(dst_object, dst_field, cast_fct(value))
        return dst_object
