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

from datetime import datetime
from mock import Mock, patch
from xivo_recording.services import manager_utils
import copy
import unittest
from xivo_dao.agentfeaturesdao import AgentFeaturesDAO


class FakeDate(datetime):
        "A manipulable date replacement"
        def __init__(self):
            pass

        @classmethod
        def now(cls):
            return datetime(year=2012, month=1, day=1)


class TestCampagneManagement(unittest.TestCase):

    def mock_reconnectable(self, attribute_name):
        def reconnector(func):
            return func
        return reconnector

    def setUp(self):

        manager_utils.reconnectable = self.mock_reconnectable

        self.patcher_datetime = patch("datetime.datetime", FakeDate)
        mock_patch_datetime = self.patcher_datetime.start()
        self.instance_datetime = FakeDate
        mock_patch_datetime.return_value = self.instance_datetime

        from xivo_recording.services.recording_management import RecordingManagement
        self._recordingManager = RecordingManagement()
        self._recordingManager.recording_details_db = Mock()
        self._recordingManager.agentFeatDao = Mock()

    def test_add_recording(self):
        campaign_id = 1
        data = {
            "cid": '001',
            "caller": '2002',
            "agent_no": '1000'
        }
        self._recordingManager.agentFeatDao.agent_id.return_value = '1'

        self._recordingManager.recording_details_db.add_recording\
                    .return_value = True
        result = self._recordingManager.add_recording(campaign_id, data)

        del data["agent_no"]
        data["agent_id"] = '1'
        data['campaign_id'] = str(campaign_id)

        self.assertTrue(result)
        self._recordingManager.recording_details_db.add_recording\
                    .assert_called_with(data)

    def test_get_recordings_as_dict(self):
        campaign_id = 1
        search = {'cid': '111',
                  'caller': '2002',
                  'agent_no': '1000'}
        dao_result = {'total': 1,
                      'data': [{'cid': '111',
                                'caller': '2002',
                                'agent_id': '1'}]}
        expected_result = copy.deepcopy(dao_result)
        expected_result['data'][0]['agent_no'] = '1000'
        self._recordingManager.recording_details_db.get_recordings_as_list\
                       .return_value = dao_result
        self._recordingManager.agentFeatDao.agent_number.return_value = '1000'
        self._recordingManager.agentFeatDao.agent_id.return_value = '1'

        result = self._recordingManager.get_recordings_as_dict(campaign_id,
                                                               search, None)
        del search['agent_no']
        search['agent_id'] = '1'
        self.assertDictEqual(result, expected_result)
        self._recordingManager.recording_details_db.get_recordings_as_list\
                    .assert_called_with(campaign_id, search, None)
