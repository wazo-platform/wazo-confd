# -*- coding: UTF-8 -*-

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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..


import unittest
from mock import Mock, patch
from rest import flask_http_server
from recording_config import RecordingConfig
import random
from services.campagne_management import CampagneManagement

mock_campagne_management = Mock(CampagneManagement)


class TestFlaskHttpServer(unittest.TestCase):

    def setUp(self):
        self.app = flask_http_server.app.test_client()

    @patch("services.campagne_management.campagne_manager", mock_campagne_management)
    def test_get_campaigns(self):
        data = {}
        status = "200 OK"
        mock_campagne_management.get_campagnes_as_dict.return_value = data

        result = self.app.get(RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RecordingConfig.XIVO_RECORDING_SERVICE_PATH +
                              "/")

        self.assertEqual(status, result.status)
        print result.data

        mock_campagne_management.get_campagnes_as_dict.assert_called_with()

    @patch("services.campagne_management.campagne_manager", mock_campagne_management)
    def test_add_campaign(self):
        status = "200 OK"

        unique_id = str(random.randint(10000, 99999999))
        campagne_name = "campagne-" + unique_id
        queue_name = "prijem"
        base_filename = campagne_name + "-"

        data = {
            "unique_id": unique_id,
            "campagne_name": campagne_name,
            "activated": False,
            "base_filename": base_filename,
            "queue_name": queue_name
        }

        mock_campagne_management.get_campagnes_as_dict.return_value = data

        result = self.app.get(RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RecordingConfig.XIVO_RECORDING_SERVICE_PATH +
                              "/")

        self.assertEqual(status, result.status)

        mock_campagne_management.get_campagnes_as_dict.assert_called()
