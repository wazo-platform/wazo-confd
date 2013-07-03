# -*- coding: UTF-8 -*-
#
# Copyright (C) 2012  Avencall
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

import unittest
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_restapi.v1_0.service_data_model.line_sdm import LineSdm
from xivo_restapi.v1_0.mapping_alchemy_sdm.line_mapping import LineMapping


class TestLineMapping(unittest.TestCase):

    def setUp(self):
        self.line_alchemy = LineFeatures()
        self.line_sdm = LineSdm()
        self.line_alchemy.number = self.line_sdm.number = "1234"
        self.line_mapping = LineMapping()

    def test_alchemy_to_sdm(self):
        result = self.line_mapping.alchemy_to_sdm(self.line_alchemy)
        self.assertEquals(self.line_sdm.__dict__, result.__dict__)

    def test_sdm_to_alchemy(self):
        result = self.line_mapping.sdm_to_alchemy(self.line_sdm)
        self.assertEquals(self.line_alchemy.todict(), result.todict())

    def test_sdm_to_alchemy_dict(self):
        line_dict_sdm = {}
        line_dict_alchemy = {}
        line_dict_sdm['number'] = "1234"
        line_dict_alchemy['number'] = "1234"

        result = self.line_mapping.sdm_to_alchemy_dict(line_dict_sdm)
        self.assertEquals(line_dict_alchemy, result)
