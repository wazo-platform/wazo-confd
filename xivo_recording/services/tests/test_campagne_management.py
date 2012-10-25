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
from services.campagne_management import CampagneManagement
from mock import Mock
import random


class TestCampagneManagement(unittest.TestCase):

    def setUp(self):
        self._campagneManager = CampagneManagement()
        self._campagneManager.record_db = Mock()

    def test_campagne_creation(self):
        campaignName = "test-campagne" + str(random.randint(10, 99))
        queue_name = "prijem"
        base_filename = queue_name + "-" + campaignName + "-"

        params = {
            "base_filename": base_filename,
            "queue_name": queue_name
        }

        expected_params = params.copy()

        expected_params["uniqueid"] = campaignName

        self._campagneManager.record_db.insert_into(expected_params)

        self._campagneManager.create_campagne(campaignName, params)
        self._campagneManager.record_db.insert_into.assert_called_with(expected_params)



