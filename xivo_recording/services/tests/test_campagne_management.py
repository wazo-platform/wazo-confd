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
import random
from mock import Mock
from xivo_recording.services.campagne_management import CampagneManagement


class TestCampagneManagement(unittest.TestCase):

    def setUp(self):
        self._campagneManager = CampagneManagement()
        self._campagneManager.record_db = Mock()
        self._campaignName = "test-campagne" + str(random.randint(10, 99))

    def test_create_campaign(self):
        unique_id = str(random.randint(10000, 99999999))
        campagne_name = "campagne-" + unique_id
        queue_id = "1"
        base_filename = campagne_name + "-"

        data = {
            "campagne_name": campagne_name,
            "activated": False,
            "base_filename": base_filename,
            "queue_id": queue_id
        }
        self._campagneManager.record_db.add.return_value = True

        self.assertTrue(self._campagneManager._create_campaign(data))

        self._campagneManager.record_db.add.assert_called_with(data)

    def test_get_campaigns_as_dict(self):
        unique_id = str(random.randint(10000, 99999999))
        campagne_name = "campagne-" + unique_id
        queue_id = "1"
        base_filename = campagne_name + "-"

        data = {
            "campagne_name": campagne_name,
            "activated": False,
            "base_filename": base_filename,
            "queue_id": queue_id
        }
        self._campagneManager.record_db.get_records_as_dict.return_value = data

        self.assertEqual(self._campagneManager._get_campaigns_as_dict(), data)
