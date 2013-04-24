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
from xivo_dao import agent_dao, recordings_dao
from xivo_dao.alchemy.recordings import Recordings
from xivo_restapi.restapi_config import RestAPIConfig
from xivo_restapi.services.utils.exceptions import InvalidInputException
import os
import unittest


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
        self.patcher_datetime = patch("datetime.datetime", FakeDate)
        mock_patch_datetime = self.patcher_datetime.start()
        self.instance_datetime = FakeDate
        mock_patch_datetime.return_value = self.instance_datetime

        from xivo_restapi.services.recording_management import RecordingManagement
        self._recordingManager = RecordingManagement()

    def test_add_recording(self):
        campaign_id = 1
        recording = Recordings()
        agent_dao.agent_id = Mock()
        agent_dao.agent_id.return_value = '1'

        recordings_dao.add_recording = Mock()
        recordings_dao.add_recording.return_value = True
        result = self._recordingManager.add_recording(campaign_id, recording)

        self.assertTrue(result)
        recordings_dao.add_recording.assert_called_with(recording)

    def test_add_recording_no_agent(self):
        campaign_id = 1
        recording = Recordings()
        recording.agent_no = '2000'
        agent_dao.agent_id = Mock()
        agent_dao.agent_id.side_effect = LookupError('')

        self.assertRaises(InvalidInputException, self._recordingManager.add_recording,
                          campaign_id, recording)

    def test_get_recordings(self):
        campaign_id = 1
        search = {'cid': '111',
                  'caller': '2002',
                  'agent_no': '1000'}
        dao_result = (1, [Recordings()])
        recordings_dao.get_recordings = Mock()
        recordings_dao.get_recordings.return_value = dao_result
        agent_dao.agent_number = Mock()
        agent_dao.agent_number.return_value = '1000'
        agent_dao.agent_id = Mock()
        agent_dao.agent_id.return_value = '1'

        result = self._recordingManager.get_recordings(campaign_id,
                                                               search, None)
        del search['agent_no']
        search['agent_id'] = '1'
        self.assertEquals(result, dao_result)
        self.assertEqual(result[1][0].agent_no, '1000')
        recordings_dao.get_recordings.assert_called_with(campaign_id, search, None)

    def test_get_recordings_paginated(self):
        campaign_id = 1
        search = {'cid': '111',
                  'caller': '2002',
                  'agent_no': '1000'}
        dao_result = (1, [Recordings()])
        recordings_dao.get_recordings = Mock()
        recordings_dao.get_recordings.return_value = dao_result
        agent_dao.agent_number = Mock()
        agent_dao.agent_number.return_value = '1000'
        agent_dao.agent_id = Mock()
        agent_dao.agent_id.return_value = '1'

        result = self._recordingManager.get_recordings(campaign_id,
                                                       search,
                                                       (1, 20))
        del search['agent_no']
        search['agent_id'] = '1'
        self.assertEqual(result, dao_result)
        self.assertEqual(result[1][0].agent_no, '1000')
        recordings_dao.get_recordings.assert_called_with(campaign_id, search, (1, 20))

    def test_search_recordings_paginated(self):
        campaign_id = 1
        search = {'key': '2002',
                  'foo': 'bar'}
        dao_result = (1, [Recordings()])
        recordings_dao.search_recordings = Mock()
        recordings_dao.search_recordings.return_value = dao_result
        agent_dao.agent_number = Mock()
        agent_dao.agent_number.return_value = '1000'

        result = self._recordingManager.search_recordings(campaign_id,
                                                          search,
                                                          (1, 20))
        self.assertEqual(result, dao_result)
        self.assertEqual(result[1][0].agent_no, '1000')
        recordings_dao.search_recordings.assert_called_with(campaign_id, '2002', (1, 20))

    def test_search_recordings(self):
        campaign_id = 1
        search = {'key': '2002',
                  'foo': 'bar'}
        dao_result = (1, [Recordings()])
        recordings_dao.search_recordings = Mock()
        recordings_dao.search_recordings.return_value = dao_result
        agent_dao.agent_number = Mock()
        agent_dao.agent_number.return_value = '1000'

        result = self._recordingManager.search_recordings(campaign_id,
                                                               search, None)
        self.assertEqual(result, dao_result)
        self.assertEqual(result[1][0].agent_no, '1000')
        recordings_dao.search_recordings.assert_called_with(campaign_id, '2002', None)

    def test_delete(self):
        campaign_id = 1
        cid = '001'
        filename = 'filename.wav'
        recordings_dao.delete = Mock()
        recordings_dao.delete.return_value = filename
        os.remove = Mock()
        self.assertTrue(self._recordingManager.delete(campaign_id, cid))
        recordings_dao.delete.assert_called_with(campaign_id, cid)
        os.remove.assert_called_with(RestAPIConfig.RECORDING_FILE_ROOT_PATH + \
                         '/' + filename)
