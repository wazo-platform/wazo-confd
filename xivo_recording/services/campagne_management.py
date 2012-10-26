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


class CampagneManagement(object):

    def __init__(self):

        dbconnection.unregister_db_connection_pool()
        dbconnection.register_db_connection_pool(dbconnection.DBConnectionPool(dbconnection.DBConnection))
        dbconnection.add_connection(RecordingConfig.RECORDING_DB_URI)

        self.record_db = RecordCampaignDbBinder.new_from_uri(RecordingConfig.RECORDING_DB_URI)

    def create_campagne(self, name, params):
        params["uniqueid"] = name
        self.record_db.add(params)

    def get_campagne(self, name):
        pass


