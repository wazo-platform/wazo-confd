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

from xivo_recording.recording_config import RecordingConfig
import random
import time
from xivo_recording.rest import rest_encoder


class RestCampaign(object):

    def __init__(self):
        unique_id = "lettuce" + time.ctime() + str(random.randint(10000, 99999999))
        queue_name = "queue_" + str(1)
        base_filename = unique_id + "-" + str(queue_name) + "-"

        self.campaign = {
            "campaign_name": unique_id,
            "base_filename": base_filename,
            "activated": True,
            "queue_name": queue_name
        }

        self.recording = {}

    def create(self, campaign_name, queue_id=1):
        connection = httplib.HTTPConnection(
                                RecordingConfig.XIVO_RECORD_SERVICE_ADDRESS +
                                ":" +
                                str(RecordingConfig.XIVO_RECORD_SERVICE_PORT)
                            )

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/"

        self.campaign["campaign_name"] = campaign_name
        self.campaign["queue_id"] = queue_id
        body = rest_encoder.encode(self.campaign)
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        connection.request("POST", requestURI, body, headers)

        reply = connection.getresponse()

        # TODO : Verify the Content-type
        # replyHeader = reply.getheaders()

        assert reply.status == 201

        return reply.read()

    def list(self):
        connection = httplib.HTTPConnection(
                                RecordingConfig.XIVO_RECORD_SERVICE_ADDRESS +
                                ":" +
                                str(RecordingConfig.XIVO_RECORD_SERVICE_PORT)
                            )

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/"

        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        connection.request("GET", requestURI, "", headers)
        reply = connection.getresponse()

        body = reply.read()

        campaigns = rest_encoder.decode(body)

        result = False
        for campaign in campaigns:
            for attribute in self.campaign:
                if (attribute in campaign):
                    result = True
                    break

        assert result
#        return result
        return campaigns

    def get_activated_campaigns(self, queue_id):
        connection = httplib.HTTPConnection(
                                RecordingConfig.XIVO_RECORD_SERVICE_ADDRESS +
                                ":" +
                                str(RecordingConfig.XIVO_RECORD_SERVICE_PORT)
                            )

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/" + \
                        "?activated=true&queue_id=" + str(queue_id)

        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        connection.request("GET", requestURI, "", headers)
        reply = connection.getresponse()

        body = reply.read()

        campaigns = rest_encoder.decode(body)

        return campaigns

    def addRecordingDetails(self, campaign_id, callid, caller, callee, time, queue_name):
        connection = httplib.HTTPConnection(
                                RecordingConfig.XIVO_RECORD_SERVICE_ADDRESS +
                                ":" +
                                str(RecordingConfig.XIVO_RECORD_SERVICE_PORT)
                            )

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + \
                        "/" + str(campaign_id) + '/'

        self.recording['cid'] = callid
        self.recording['caller'] = caller
        self.recording['callee'] = callee
        self.recording['time'] = time
        self.recording['queue_name'] = queue_name
        body = rest_encoder.encode(self.recording)
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        connection.request("POST", requestURI, body, headers)

        reply = connection.getresponse()
        print("\nreply: " + reply.read() + '\n')

        # TODO : Verify the Content-type
        # replyHeader = reply.getheaders()

        assert reply.status == 201
        return (reply.status == 201)

    def verifyRecordingsDetails(self, campaign_id):
        connection = httplib.HTTPConnection(
                                RecordingConfig.XIVO_RECORD_SERVICE_ADDRESS +
                                ":" +
                                str(RecordingConfig.XIVO_RECORD_SERVICE_PORT)
                            )

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + \
                        '/' + str(campaign_id) + "/"

        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        connection.request("GET", requestURI, "", headers)
        reply = connection.getresponse()

        body = reply.read()
        assert body != None, "No result" 
        recordings = rest_encoder.decode(body)

        result = False
        for recording in recordings:
            if (recording["cid"] == self.recording['cid']):
                result = True

        assert result
        return result

    def update(self, campaign_id, params):
        connection = httplib.HTTPConnection(
                                RecordingConfig.XIVO_RECORD_SERVICE_ADDRESS +
                                ":" +
                                str(RecordingConfig.XIVO_RECORD_SERVICE_PORT)
                            )

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/" + \
                        campaign_id
        print "URI for update: " + requestURI
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE
        body = rest_encoder.encode(params)
        connection.request("PUT", requestURI, body, headers)
        reply = connection.getresponse()
        return reply.status == 200 or reply.status == 201
    
    def getCampaign(self, campaign_name):
        connection = httplib.HTTPConnection(
                                RecordingConfig.XIVO_RECORD_SERVICE_ADDRESS +
                                ":" +
                                str(RecordingConfig.XIVO_RECORD_SERVICE_PORT)
                            )

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/" + \
                        campaign_name

        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE
        connection.request("GET", requestURI, '', headers)
        reply = connection.getresponse()
        return rest_encoder.decode(reply.read())