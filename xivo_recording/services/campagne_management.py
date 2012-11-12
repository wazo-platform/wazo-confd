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

from xivo_dao.alchemy import dbconnection
from recording_config import RecordingConfig
from dao.record_campaign_dao import RecordCampaignDbBinder
from sqlalchemy.exc import OperationalError
import logging

logger = logging.getLogger(__name__)


class CampagneManagement(object):

    def __init__(self):
        self.__init_db_connection()

    def __init_db_connection(self):
        dbconnection.unregister_db_connection_pool()
        dbconnection.register_db_connection_pool(dbconnection.DBConnectionPool(dbconnection.DBConnection))
        dbconnection.add_connection(RecordingConfig.RECORDING_DB_URI)

        self.record_db = RecordCampaignDbBinder.new_from_uri(RecordingConfig.RECORDING_DB_URI)

    def create_campagne(self, params):
        result = None
        try:
            result = self.record_db.add(params)
        except Exception as e:
            result = "Impossible to add the campagin: " + str(e)
        return result

    def get_campagne(self, name):
        try:
            result = self.record_db.get_records()
        except OperationalError:
            # if the database was restarted we need to reconnect
            try:
                self.__init_db_connection()
                result = self.record_db.get_records()
            except Exception as e:
                logger.critical("Database connection failure!")
                #TODO custom exceptions
                raise e
        return result

    def get_campagnes_as_dict(self):
        try:
            result = self.record_db.get_records_as_dict()
        except OperationalError:
            # if the database was restarted we need to reconnect
            try:
                self.__init_db_connection()
                result = self.record_db.get_records_as_dict()
            except Exception as e:
                logger.critical("Database connection failure!")
                #TODO custom exceptions
                raise e
        return result

