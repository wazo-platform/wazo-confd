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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


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

from xivo_dao.agentfeaturesdao import AgentFeaturesDAO
from xivo_recording.dao.recording_details_dao import RecordingDetailsDbBinder
from xivo_recording.services.manager_utils import _init_db_connection, \
    reconnectable
import logging
import os
from commands import getoutput

logger = logging.getLogger(__name__)


class RecordingManagement:

    def __init__(self):
        self.recording_details_db = _init_db_connection(RecordingDetailsDbBinder)
        self.agentFeatDao = AgentFeaturesDAO(self.recording_details_db.session)

    @reconnectable("recording_details_db")
    def add_recording(self, campaign_id, params):
        """
        Converts data to the final format and calls the DAO
        """
        logger.debug("Add_recording: " + str(campaign_id) + ", " + str(params))
        recording_details = {}
        for item in params:
            if (item == 'agent_no'):
                agent_id = self.agentFeatDao.agent_id(params['agent_no'])
                logger.debug("Replacing agent number: " + params['agent_no'] + " by agent id: " + agent_id)
                recording_details["agent_id"] = agent_id
            else:
                recording_details[item] = params[item]

        recording_details['campaign_id'] = str(campaign_id)
        result = self.recording_details_db.add_recording(recording_details)
        return result

    @reconnectable("recording_details_db")
    def get_recordings_as_dict(self, campaign_id, search=None):
        logger.debug("get_recordings_as_dict")
        search_pattern = {}
        for item in search:
            if (item == 'agent_no'):
                search_pattern["agent_id"] = self.agentFeatDao.agent_id(search['agent_no'])
            else:
                search_pattern[item] = search[item]
        result = self.recording_details_db. \
                            get_recordings_as_list(campaign_id, search_pattern)
        return self.insert_agent_no(result)

    @reconnectable("recording_details_db")
    def search_recordings(self, campaign_id, search):
        logger.debug("search_recordings")
        if(search == None or search == {} or 'key' not in search):
            return self.get_recordings_as_dict(campaign_id)
        else:
            result = self.recording_details_db.search_recordings(campaign_id, search['key'])
            return self.insert_agent_no(result)

    def insert_agent_no(self, liste):
        for row in liste:
            agent_no = ''
            for column in row:
                if column == 'agent_id':
                    agent_no = self.agentFeatDao.agent_number(row[column])
            row['agent_no'] = agent_no
        return liste

    @reconnectable("recording_details_db")
    def delete(self, campaign_id, recording_id):
        filename = self.recording_details_db.delete(campaign_id, recording_id)
        if(filename == None):
            return False
        else:
            logphrase = "File " + filename + " is being deleted."
            getoutput('logger -t xivo-recording "' + logphrase + '"')
            os.remove("/var/lib/pf-xivo/sounds/campagnes/" + filename)
            return True

    def supplement_add_input(self, data):
        '''Returns the supplemented input'''
        logger.debug("Supplementing input for 'add_recording'")
        for key in data:
            if(data[key] == ''):
                data[key] = None
        return data
