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

import logging
from sqlalchemy.exc import OperationalError
from xivo_dao.alchemy import dbconnection
from xivo_recording.dao.exceptions import DataRetrieveError
from xivo_recording.dao.record_campaign_dao import RecordCampaignDbBinder
from xivo_recording.recording_config import RecordingConfig
from xivo_dao import queue_features_dao
from xivo_recording.dao.recording_details_dao import RecordingDetailsDbBinder

logger = logging.getLogger(__name__)


class CampagneManagement(object):

    def __init__(self):
        self.__init_db_connection()

    def __init_db_connection(self):
        dbconnection.unregister_db_connection_pool()
        dbconnection.register_db_connection_pool(dbconnection.DBConnectionPool(dbconnection.DBConnection))
        dbconnection.add_connection(RecordingConfig.RECORDING_DB_URI)
        dbconnection.add_connection_as(RecordingConfig.RECORDING_DB_URI, 'asterisk')
        self.record_db = RecordCampaignDbBinder.new_from_uri(RecordingConfig.RECORDING_DB_URI)
        self.recording_details_db = RecordingDetailsDbBinder.new_from_uri(RecordingConfig.RECORDING_DB_URI)

    def create_campaign(self, params):
        result = None
        try:
            result = self.record_db.add(params)
        except Exception as e:
            result = "Impossible to add the campagin: " + str(e)
        return result

    def get_campaigns_as_dict(self, search=None):
        """
        Calls the DAO and converts data to the final format
        """
        result = self._get_campaigns_as_dict(search)

        try:
            for item in result:
                item["queue_name"] = queue_features_dao. \
                                        queue_name(item["queue_id"])
        except Exception as e:
            logger.critical("DAO failure(" + str(e) + ")!")
            raise DataRetrieveError("DAO failure(" + str(e) + ")!")

        return result

    def _get_campaigns_as_dict(self, search=None):
        logger.debug("get_campaigns_as_dict")

        try:
            result = self.record_db.get_records_as_dict(search)
        except OperationalError:
            # if the database was restarted we need to reconnect
            try:
                self.__init_db_connection()
                result = self.record_db.get_records_as_dict(search)
            except Exception:
                logger.critical("Database connection failure!")
                raise DataRetrieveError("Database connection failure")

        return result
    
    def update_campaign(self, original_campaign_name, params):
        result = None
        try:
            logger.debug('going to update')
            result = self.record_db.update(original_campaign_name, params)
        except Exception as e:
            result = "Impossible to update the campagin: " + str(e)
        return result
        
        