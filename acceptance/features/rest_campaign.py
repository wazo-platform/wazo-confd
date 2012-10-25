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

from gevent import httplib

from recording_config import RecordingConfig
from xivo_cti_protocol import cti_encoder
import random
import time


class RestCampaign(object):

    def __init__(self):
        uniqueid = "lettuce" + time.ctime() + str(random.randint(10000, 99999999))
        queue_name = "prijem"
        base_filename = queue_name + "-" + uniqueid + "-"

        self.campagne = {
#            "uniqueid": uniqueid,
            "base_filename": base_filename,
            "queue_name": queue_name
        }

    def create(self, campaign_name):
        connection = httplib.HTTPConnection(RecordingConfig.XIVO_RECORD_SERVICE_ADDRESS + ":" + str(RecordingConfig.XIVO_RECORD_SERVICE_PORT))
        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/" + campaign_name + "?sd=w&dew=1"

#        self.campagne["uniqueid"] = campaign_name
        body = cti_encoder.encode(self.campagne)
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        connection.request("POST", requestURI, body, headers)

        reply = connection.getresponse()
        print("\nreply: " + reply.read() + '\n')
        replyHeader = reply.getheaders()

        #assert rHeader ==

        return False
