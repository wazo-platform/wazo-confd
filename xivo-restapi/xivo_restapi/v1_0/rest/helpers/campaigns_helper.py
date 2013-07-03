# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from datetime import datetime
from xivo_dao.alchemy.record_campaigns import RecordCampaigns
from xivo_restapi.v1_0.rest.helpers import global_helper
from xivo_restapi.v1_0.rest.helpers.global_helper import str_to_datetime
import logging

logger = logging.getLogger()


class CampaignsHelper():

    def supplement_add_input(self, data):
        '''Returns the supplemented input for add'''
        logger.debug("Supplementing input for 'add'")
        for key in data:
            if data[key] == '':
                data[key] = None
        if "start_date" not in data or data["start_date"] is None:
            data["start_date"] = datetime.now().strftime("%Y-%m-%d")
        if "end_date" not in data or data["end_date"] is None:
            data["end_date"] = datetime.now().strftime("%Y-%m-%d")
        return data

    def supplement_edit_input(self, data):
        '''Returns the supplemented input for edit'''
        for key in data:
            if data[key] == '':
                data[key] = None
        return data

    def create_instance(self, data):
        instance = global_helper.create_class_instance(RecordCampaigns, data)
        instance.start_date = str_to_datetime(instance.start_date)
        instance.end_date = str_to_datetime(instance.end_date)
        return instance
