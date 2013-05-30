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

from acceptance.features.steps.helpers.rest_queues import RestQueues
from acceptance.features.steps.helpers.ws_utils import WsUtils
from xivo_dao import agent_dao, queue_dao, record_campaigns_dao, recordings_dao
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_lettuce.ssh import SSHClient
from xivo_restapi.restapi_config import RestAPIConfig
import datetime


class RestCampaign(object):

    def __init__(self):
        self.ws_utils = WsUtils()

    def create(self, campaign_name, queue_name='test', activated=True,
               start_date=None, end_date=None, campaign_id=None):

        self.queue_create_if_not_exists(queue_name)

        campaign = {
            "campaign_name": campaign_name,
            "base_filename": "%s-file-" % campaign_name,
            "queue_id": queue_dao.id_from_name(queue_name),
            "activated": activated
        }

        if start_date is not None:
            campaign["start_date"] = str(start_date)
        if end_date is not None:
            campaign["end_date"] = str(end_date)
        if campaign_id is not None:
            campaign['id'] = campaign_id

        url = "%s/" % RestAPIConfig.XIVO_RECORDING_SERVICE_PATH
        reply = self.ws_utils.rest_post(url, campaign)
        return reply

    def list(self):
        url = "%s/" % RestAPIConfig.XIVO_RECORDING_SERVICE_PATH
        reply = self.ws_utils.rest_get(url)
        return reply

    def get_activated_campaigns(self, queue_id):
        url = "%s/?activated=true&queue_id=%s" % (
            RestAPIConfig.XIVO_RECORDING_SERVICE_PATH,
            queue_id
        )

        reply = self.ws_utils.rest_get(url)
        return reply

    def addRecordingDetails(self, campaign_id, callid, caller, agent_no, time):
        recording = {
            'cid': callid,
            'caller': caller,
            'agent_no': agent_no,
            'start_time': time,
            'end_time': time,
            'filename': "%s.wav" % callid
        }

        url = "%s/%s/" % (RestAPIConfig.XIVO_RECORDING_SERVICE_PATH, campaign_id)

        reply = self.ws_utils.rest_post(url, recording)

        #we create the file
        dirname = RestAPIConfig.RECORDING_FILE_ROOT_PATH
        config_file = open("config.ini", "r")
        remote_host = config_file.read()
        config_file.close()
        remote_host = remote_host.rstrip()
        file_path = dirname + "/" + recording['filename']
        cmd = ['touch', file_path]
        sshclient = SSHClient('root', remote_host)
        sshclient.call(cmd)
        return reply

    def verifyRecordingsDetails(self, campaign_id, callid):
        url = "%s/%s/" % (RestAPIConfig.XIVO_RECORDING_SERVICE_PATH, campaign_id)
        reply = self.ws_utils.rest_get(url)

        assert reply.data is not None, "No result"
        recordings = reply.data['items']

        result = False
        for recording in recordings:
            if (recording["cid"] == callid):
                result = True
        return result

    def updateCampaign(self, campaign_id, params):
        url = "%s/%s" % (RestAPIConfig.XIVO_RECORDING_SERVICE_PATH, campaign_id)
        reply = self.ws_utils.rest_put(url, params)
        return reply.status == 200 or reply.status == 201

    def get_campaign(self, campaign_id):
        url = "%s/%s" % (RestAPIConfig.XIVO_RECORDING_SERVICE_PATH, campaign_id)
        return self.ws_utils.rest_get(url)

    def get_running_activated_campaigns_for_queue(self, queue_id):
        url = "%s/?activated=true&running=true&queue_id=%s" % (
            RestAPIConfig.XIVO_RECORDING_SERVICE_PATH,
            queue_id
        )
        reply = self.ws_utils.rest_get(url)
        return reply

    def create_if_not_exists(self, campaign_name):
        result = record_campaigns_dao.id_from_name(campaign_name)
        if result is None:
            rest_queues = RestQueues()
            rest_queues.create_if_not_exists('test', 1)
            result = self.create(campaign_name,
                                 'test',
                                 True,
                                 datetime.datetime.now().strftime("%Y-%m-%d"),
                                 datetime.datetime.now().strftime("%Y-%m-%d"))
            return type(result.data) == int and result.data > 0
        return True

    def queue_create_if_not_exists(self, queue_name):
        if not queue_dao.is_a_queue(queue_name):
            queue = QueueFeatures()
            queue.name = queue_name
            queue.displayname = queue_name

            queue_dao.add_queue(queue)
            return queue_dao.is_a_queue(queue_name)
        else:
            return True

    def add_agent_if_not_exists(self, agent_no, numgroup=1, firstname="FirstName",
                                lastname="LastName", context="default", language="fr_FR"):
        try:
            agent_id = agent_dao.agent_id(agent_no)
            return agent_id
        except LookupError:
            agent_features = AgentFeatures()
            agent_features.numgroup = numgroup
            agent_features.firstname = firstname
            agent_features.lastname = lastname
            agent_features.number = agent_no
            agent_features.passwd = agent_no
            agent_features.context = context
            agent_features.language = language
            agent_features.commented = 0
            agent_features.description = "description"

            agent_dao.add_agent(agent_features)
            return agent_features.id

    def agent_exists(self, agent_no):
        try:
            agent_id = agent_dao.agent_id(agent_no)
            return agent_id
        except LookupError:
            return 0
        return -1

    def search_recordings(self, campaign_id, key=None):
        serviceURI = "%s/%s/search" % (
            RestAPIConfig.XIVO_RECORDING_SERVICE_PATH,
            campaign_id
        )

        if key is not None:
            serviceURI += "?key=%s" % key

        return self.ws_utils.rest_get(serviceURI)

    def deleteRecording(self, campaign_id, callid):
        #os.chmod(RestAPIConfig.RECORDING_FILE_ROOT_PATH, 0777)
        url = "%s/%s/%s" % (
            RestAPIConfig.XIVO_RECORDING_SERVICE_PATH,
            campaign_id,
            callid
        )

        reply = self.ws_utils.rest_delete(url)
        return reply

    def delete_agent(self, agent_no):
        try:
            agent_id = agent_dao.agent_id(agent_no)
            print "\nAgent id: " + agent_id + "\n"
            agent_dao.del_agent(agent_id)
            return True
        except Exception as e:
            print "\nException raised: " + str(e) + "\n"
            return False

    def create_with_errors(self, campaign_name, queue_name='test',
                           activated=True, start_date=None,
                           end_date=None, campaign_id=None):

        self.queue_create_if_not_exists(queue_name)
        campaign = {
            "campaign_name": campaign_name,
            "base_filename": "%s-file-" % campaign_name,
            "queue_id": queue_dao.id_from_name(queue_name),
            "activated": activated
        }

        if start_date is not None:
            campaign["start_date"] = str(start_date)
        if end_date is not None:
            campaign["end_date"] = str(end_date)
        if campaign_id is not None:
            campaign['id'] = campaign_id

        url = "%s/" % RestAPIConfig.XIVO_RECORDING_SERVICE_PATH
        reply = self.ws_utils.rest_post(url)

        return reply

    def paginated_list(self, page_number, page_size):
        url = "%s/?_page=%s&_pagesize=%s" % (
            RestAPIConfig.XIVO_RECORDING_SERVICE_PATH,
            page_number,
            page_size
        )

        reply = self.ws_utils.rest_get(url)
        return reply

    def paginated_recordings_list(self, campaign_id, page_number, page_size):
        url = "%s/%s/?_page=%s&_pagesize=%s" % (
            RestAPIConfig.XIVO_RECORDING_SERVICE_PATH,
            campaign_id,
            page_number,
            page_size
        )

        return self.ws_utils.rest_get(url)

    def search_paginated_recordings(self, campaign_id, key, page, pagesize):
        url = "%s/%s/search?key=%s&_page=%s&_pagesize=%s" % (
            RestAPIConfig.XIVO_RECORDING_SERVICE_PATH,
            campaign_id,
            key,
            page,
            pagesize
        )

        reply = self.ws_utils.rest_get(url)
        return reply

    def delete_all_campaigns(self):
        recordings_dao.delete_all()
        record_campaigns_dao.delete_all()

    def get_queue(self, queue_name):
        queue_id = queue_dao.id_from_name(queue_name)
        return queue_dao.get(queue_id)

    def delete_campaign(self, campaign_id):
        url = "%s/%s" % (RestAPIConfig.XIVO_RECORDING_SERVICE_PATH, campaign_id)
        reply = self.ws_utils.rest_delete(url)
        return reply
