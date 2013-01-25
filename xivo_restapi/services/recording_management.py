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

from xivo_dao import agent_dao
from xivo_restapi.dao.recording_details_dao import RecordingDetailsDbBinder
from xivo_restapi.services.manager_utils import _init_db_connection, \
    reconnectable
import logging
import os
from commands import getoutput
from xivo_restapi.restapi_config import RestAPIConfig

logger = logging.getLogger(__name__)


class RecordingManagement:

    def __init__(self):
        self.recording_details_db = _init_db_connection(RecordingDetailsDbBinder)

    @reconnectable("recording_details_db")
    def add_recording(self, campaign_id, params):
        """
        Converts data to the final format and calls the DAO
        """
        logger.debug("Add_recording: " + str(campaign_id) + ", " + str(params))
        recording_details = {}
        for item in params:
            if (item == 'agent_no'):
                agent_id = agent_dao.agent_id(params['agent_no'])
                logger.debug("Replacing agent number: " + params['agent_no'] + \
                             " by agent id: " + agent_id)
                recording_details["agent_id"] = agent_id
            else:
                recording_details[item] = params[item]

        recording_details['campaign_id'] = str(campaign_id)
        result = self.recording_details_db.add_recording(recording_details)
        return result

    @reconnectable("recording_details_db")
    def get_recordings_as_dict(self, campaign_id, search=None, technical_params=None):
        logger.debug("get_recordings_as_dict")
        search_pattern = {}
        if(search != None):
            for item in search:
                if (item == 'agent_no'):
                    search_pattern["agent_id"] = agent_dao\
                                            .agent_id(search['agent_no'])
                else:
                    search_pattern[item] = search[item]
        paginator = self._get_paginator(technical_params)
        result = self.recording_details_db. \
                            get_recordings_as_list(campaign_id,
                                                   search_pattern,
                                                   paginator)
        self.insert_agent_no(result['data'])
        return result

    @reconnectable("recording_details_db")
    def search_recordings(self, campaign_id, search, technical_params):
        logger.debug("search_recordings")
        if(search == None or search == {} or 'key' not in search):
            return self.get_recordings_as_dict(campaign_id,
                                               {},
                                               technical_params)
        else:
            paginator = self._get_paginator(technical_params)
            result = self.recording_details_db.search_recordings(campaign_id,
                                                                 search['key'],
                                                                 paginator)
            self.insert_agent_no(result['data'])
            return result

    def insert_agent_no(self, liste):
        for row in liste:
            agent_no = ''
            for column in row:
                if column == 'agent_id':
                    agent_no = agent_dao.agent_number(row[column])
            row['agent_no'] = agent_no
        return liste

    @reconnectable("recording_details_db")
    def delete(self, campaign_id, recording_id):
        filename = self.recording_details_db.delete(campaign_id, recording_id)
        if(filename == None):
            logger.error("Recording file remove error - no filename!")
            return False
        else:
            logger.debug("Deleting file: " + \
                         RestAPIConfig.RECORDING_FILE_ROOT_PATH + \
                         filename)

            logphrase = "File " + filename + " is being deleted."
            getoutput('logger -t xivo-recording "' + logphrase + '"')
            os.remove(RestAPIConfig.RECORDING_FILE_ROOT_PATH + "/" + \
                       filename)
            return True

    def supplement_add_input(self, data):
        '''Returns the supplemented input'''
        logger.debug("Supplementing input for 'add_recording'")
        for key in data:
            if(data[key] == ''):
                data[key] = None
        return data

    def _get_paginator(self, technical_params):
        paginator = None
        if(technical_params != None\
           and '_page' in technical_params\
           and '_pagesize' in technical_params):
            paginator = (int(technical_params['_page']),
                         int(technical_params['_pagesize']))
        logger.debug("Created paginator: " + str(paginator))
        return paginator
