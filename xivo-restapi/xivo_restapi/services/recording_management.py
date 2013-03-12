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

from commands import getoutput
from xivo_dao import agent_dao, recordings_dao
from xivo_restapi.restapi_config import RestAPIConfig
import logging
import os

logger = logging.getLogger(__name__)
data_access_logger = logging.getLogger(RestAPIConfig.DATA_ACCESS_LOGGERNAME)


class RecordingManagement:

    def __init__(self):
        pass

    def add_recording(self, campaign_id, recording):
        data_access_logger.info("Adding a recording to the campaign %d with data %s."
                                % (campaign_id, recording.todict()))
        if('agent_no' in vars(recording)):
            recording.agent_id = agent_dao.agent_id(recording.agent_no)
        recording.campaign_id = campaign_id
        result = recordings_dao.add_recording(recording)
        return result

    def get_recordings(self, campaign_id, search=None, paginator=None):
        data_access_logger.info("Getting recordings for campaign %d" % campaign_id +
                                " with search criteria %s paginated with %s"
                                % (search, paginator))
        search_pattern = {}
        if(search != None):
            for item in search:
                if (item == 'agent_no'):
                    search_pattern["agent_id"] = agent_dao\
                                            .agent_id(search['agent_no'])
                else:
                    search_pattern[item] = search[item]
        (total, items) = recordings_dao.get_recordings(campaign_id,
                                                       search_pattern,
                                                       paginator)
        self._insert_agent_no(items)
        return (total, items)

    def search_recordings(self, campaign_id, search, paginator=None):
        data_access_logger.info("Searching recordings in campaign %d with" % campaign_id +
                                "search criteria %s paginated with %s" % (search, paginator))
        if(search == None or search == {} or 'key' not in search):
            return self.get_recordings(campaign_id,
                                               {},
                                               paginator)
        else:
            (total, items) = recordings_dao.search_recordings(campaign_id,
                                                      search['key'],
                                                      paginator)
            self._insert_agent_no(items)
            return (total, items)

    def _insert_agent_no(self, items):
        for recording in items:
            recording.agent_no = agent_dao.agent_number(recording.agent_id)
        return items

    def delete(self, campaign_id, recording_id):
        data_access_logger.info("Deleting recording of id %s in campaign %d."
                                % (recording_id, campaign_id))
        filename = recordings_dao.delete(campaign_id, recording_id)
        if(filename == None):
            logger.error("Recording file remove error - no filename!")
            return False
        else:
            logger.debug("Deleting file: " + \
                         RestAPIConfig.RECORDING_FILE_ROOT_PATH + "/" + \
                         filename)

            logphrase = "File " + filename + " is being deleted."
            getoutput('logger -t xivo-recording "' + logphrase + '"')
            os.remove(RestAPIConfig.RECORDING_FILE_ROOT_PATH + "/" + \
                       filename)
            return True
