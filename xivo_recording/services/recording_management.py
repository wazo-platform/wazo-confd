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

from xivo_recording.dao.recording_details_dao import RecordingDetailsDbBinder
from xivo_recording.services.manager_utils import _init_db_connection, \
    reconnectable
import logging

logger = logging.getLogger(__name__)


class RecordingManagement:
    
    def __init__(self):
        self.recording_details_db = _init_db_connection(RecordingDetailsDbBinder)
        #self.recording_details_db = RecordingDetailsDbBinder.new_from_uri(RecordingConfig.RECORDING_DB_URI)
    
    @reconnectable("recording_details_db")
    def add_recording(self, campaign_id, params):
        """
        Converts data to the final format and calls the DAO
        """
        params['campaign_id'] = str(campaign_id)
        result = self.recording_details_db.add_recording(params)
        return result

    @reconnectable("recording_details_db")
    def get_recordings_as_dict(self, campaign_id, search=None):
        logger.debug("get_recordings_as_dict")
        
        result = self.recording_details_db. \
                            get_recordings_as_list(campaign_id, search)

        return result
