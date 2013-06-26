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

import unittest
from xivo_restapi.v1_0.mapping_alchemy_sdm.abstract_mapping import AbstractMapping


class TestAbstractMapping(unittest.TestCase):

    def test_map_object(self):
        class MySampleClass:
            pass

        class YourSampleClass:
            pass

        class ConcreteMapping(AbstractMapping):
            pass

        object_from = MySampleClass()
        object_from.prop0_my = None
        object_from.prop1_my = 'value1'
        object_from.prop2_my = 2
        object_to = YourSampleClass()
        mapping = {'prop0_my': 'prop0_your',
                   'prop1_my': 'prop1_your',
                   'prop2_my': 'prop2_your'}

        default_values = {'prop2_your': 3,
                          'prop3_your': None,
                          'prop4_your': "c'est vache"
                          }
        cast = {
                'prop0_your': int
                }
        my_mapping = ConcreteMapping()
        my_mapping.map_attributes(object_from, object_to, mapping, cast, default_values)
        self.assertEquals(object_from.prop1_my, object_to.prop1_your)
        self.assertEquals(object_from.prop2_my, object_to.prop2_your)
        self.assertEquals(object_to.prop3_your, None)
        self.assertEquals(object_to.prop4_your, "c'est vache")
