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

from acceptance.features import cron_utils
from acceptance.features.rest_queues import RestQueues
from xivo_dao.agentfeaturesdao import AgentFeaturesDAO
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_recording.dao.record_campaign_dao import RecordCampaignDbBinder, \
    RecordCampaignDao
from xivo_recording.dao.recording_details_dao import RecordingDetailsDbBinder, \
    RecordingDetailsDao
from xivo_recording.recording_config import RecordingConfig
from xivo_recording.rest import rest_encoder
from xivo_recording.services.manager_utils import _init_db_connection
import datetime
import os
import random
from xivo_dao import queue_features_dao
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_recording.dao.helpers.dynamic_formatting import table_list_to_list_dict


class RestCampaign(object):

    def __init__(self):
        self.agentFeatDao = AgentFeaturesDAO(self.setUpDBConnection())

    def setUpDBConnection(self):
        db_connection_pool = \
            dbconnection.DBConnectionPool(dbconnection.DBConnection)

        dbconnection.register_db_connection_pool(db_connection_pool)

        uri = RecordingConfig.RECORDING_DB_URI
        dbconnection.add_connection_as(uri, 'asterisk')
        connection = dbconnection.get_connection('asterisk')
        session = connection.get_session()
        return session

    def create(self, campaign_name, queue_name='test', activated=True,
               start_date=None, end_date=None, campaign_id=None):

        connection = RecordingConfig.getWSConnection()

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/"
        self.queue_create_if_not_exists(queue_name)
        campaign = {}

        campaign["campaign_name"] = campaign_name
        campaign["base_filename"] = campaign_name + "-file-"
        campaign["queue_id"] = queue_features_dao.id_from_name(queue_name)
        campaign["activated"] = activated
        if start_date != None:
            campaign["start_date"] = str(start_date)
        if end_date != None:
            campaign["end_date"] = str(end_date)
        if campaign_id != None:
            campaign['id'] = campaign_id
        body = rest_encoder.encode(campaign)
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        connection.request("POST", requestURI, body, headers)

        reply = connection.getresponse()

        # TODO : Verify the Content-type
        # replyHeader = reply.getheaders()

        #assert reply.status == 201

        return rest_encoder.decode(reply.read())

    def list(self):
        connection = RecordingConfig.getWSConnection()

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/"

        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        connection.request("GET", requestURI, "", headers)
        reply = connection.getresponse()

        body = reply.read()

        campaigns = rest_encoder.decode(body)
        return campaigns

    def get_activated_campaigns(self, queue_id):
        connection = RecordingConfig.getWSConnection()

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/" + \
                        "?activated=true&queue_id=" + str(queue_id)

        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        connection.request("GET", requestURI, "", headers)
        reply = connection.getresponse()

        body = reply.read()

        campaigns = rest_encoder.decode(body)

        return campaigns

    def addRecordingDetails(self, campaign_id, callid, caller, agent_no, time):
        connection = RecordingConfig.getWSConnection()

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + \
                        "/" + str(campaign_id) + '/'

        recording = {}
        recording['cid'] = callid
        recording['caller'] = caller
        recording['agent_no'] = agent_no
        recording['start_time'] = time
        recording['end_time'] = time
        recording['filename'] = callid + ".wav"

        body = rest_encoder.encode(recording)
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        connection.request("POST", requestURI, body, headers)

        #we create the file
        dirname = RecordingConfig.RECORDING_FILE_ROOT_PATH
        if(not os.path.exists(dirname)):
            cron_utils.create_dir(dirname)
        myfile = open(dirname + "/" + recording['filename'], 'w')
        myfile.write('')
        myfile.close()
        # TODO : permettre au WebService de supprimer les fichiers

        reply = connection.getresponse()
        response = reply.read()

        # TODO : Verify the Content-type
        # replyHeader = reply.getheaders()

        return (reply.status, response)

    def verifyRecordingsDetails(self, campaign_id, callid):
        connection = RecordingConfig.getWSConnection()

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + \
                        '/' + str(campaign_id) + "/"

        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        connection.request("GET", requestURI, "", headers)
        reply = connection.getresponse()

        body = reply.read()
        assert body != None, "No result"
        recordings = rest_encoder.decode(body)['data']

        result = False
        for recording in recordings:
            if (recording["cid"] == callid):
                result = True
        return result

    def updateCampaign(self, campaign_id, params):
        connection = RecordingConfig.getWSConnection()

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/" + \
                        str(campaign_id)
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE
        body = rest_encoder.encode(params)
        connection.request("PUT", requestURI, body, headers)
        reply = connection.getresponse()
        return reply.status == 200 or reply.status == 201

    def getCampaign(self, campaign_id):
        connection = RecordingConfig.getWSConnection()

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/" + \
                        str(campaign_id)

        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE
        connection.request("GET", requestURI, '', headers)
        reply = connection.getresponse()
        result = rest_encoder.decode(reply.read())['data']
        if(len(result) > 0):
            return result[0]
        else:
            return None

    def getRunningActivatedCampaignsForQueue(self, queue_id):
        connection = RecordingConfig.getWSConnection()
        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/"
        parameters = "?activated=true&running=true&queue_id=" + queue_id
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE
        connection.request("GET", requestURI + parameters, '', headers)
        reply = connection.getresponse()
        return rest_encoder.decode(reply.read())

    def create_if_not_exists(self, campaign_id):
        result = self.getCampaign(campaign_id)
        if(result == None or len(result) == 0):
            rest_queues = RestQueues()
            rest_queues.create_if_not_exists(1, 'test')
            result = self.create("lettuce" +
                                 str(random.randint(100, 999)),
                                 'test',
                                 True,
                                 datetime.datetime.now().strftime("%Y-%m-%d"),
                                 datetime.datetime.now().strftime("%Y-%m-%d"),
                                 campaign_id)

            print "\n========================" + str(result) + "\n"
            return type(result) == int and result > 0
        return True

    def queue_create_if_not_exists(self, queue_name):
        if not queue_features_dao.is_a_queue(queue_name):
            queue = QueueFeatures()
            queue.name = queue_name
            queue.displayname = queue_name

            queue_features_dao.add_queue(queue)
            return queue_features_dao.is_a_queue(queue_name)
        else:
            return True

    def add_agent_if_not_exists(self, agent_no, numgroup=1, firstname="FirstName",
                                lastname="LastName", context="default", language="fr_FR"):
        try:
            agent_id = self.agentFeatDao.agent_id(agent_no)
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

            self.agentFeatDao.add_agent(agent_features)
            return agent_features.id

    def agent_exists(self, agent_no):
        try:
            agent_id = self.agentFeatDao.agent_id(agent_no)
            return agent_id
        except LookupError:
            return 0
        return -1

    def search_recordings(self, campaign_id, key=None):
        connection = RecordingConfig.getWSConnection()

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/" + \
                        str(campaign_id) + "/search"
        if(key != None):
            parameters = "?key=" + key
            requestURI += parameters
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE
        connection.request("GET", requestURI, '', headers)
        reply = connection.getresponse()
        return rest_encoder.decode(reply.read())

    def deleteRecording(self, campaign_id, callid):
        os.chmod(RecordingConfig.RECORDING_FILE_ROOT_PATH, 0777)
        connection = RecordingConfig.getWSConnection()
        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/" + \
                        str(campaign_id) + "/" + str(callid)
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE
        connection.request("DELETE", requestURI, '', headers)
        reply = connection.getresponse()
        response = rest_encoder.decode(reply.read())
        return (reply.status, response)

    def delete_agent(self, agent_no):
        try:
            agent_id = self.agentFeatDao.agent_id(agent_no)
            print "\nAgent id: " + agent_id + "\n"
            self.agentFeatDao.del_agent(agent_id)
            return True
        except Exception as e:
            print "\nException raised: " + str(e) + "\n"
            return False

    def create_with_errors(self, campaign_name, queue_name='test',
                           activated=True, start_date=None,
                           end_date=None, campaign_id=None):
        connection = RecordingConfig.getWSConnection()

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/"
        self.queue_create_if_not_exists(queue_name)
        campaign = {}

        campaign["campaign_name"] = campaign_name
        campaign["base_filename"] = campaign_name + "-file-"
        campaign["queue_id"] = queue_features_dao.id_from_name(queue_name)
        campaign["activated"] = activated
        if start_date != None:
            campaign["start_date"] = str(start_date)
        if end_date != None:
            campaign["end_date"] = str(end_date)
        if campaign_id != None:
            campaign['id'] = campaign_id
        body = rest_encoder.encode(campaign)
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        connection.request("POST", requestURI, body, headers)

        reply = connection.getresponse()

        return (reply.status, rest_encoder.decode(reply.read()))

    def paginated_list(self, page_number, page_size):
        connection = RecordingConfig.getWSConnection()

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/"
        params = "?_page=" + str(page_number) + "&_pagesize=" + str(page_size)
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        connection.request("GET", requestURI + params, "", headers)
        reply = connection.getresponse()

        body = reply.read()

        campaigns = rest_encoder.decode(body)
        return campaigns

    def paginated_recordings_list(self, campaign_id, page_number, page_size):
        connection = RecordingConfig.getWSConnection()

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + \
                        "/" + campaign_id + "/"

        params = "?_page=" + str(page_number) + "&_pagesize=" + str(page_size)
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        connection.request("GET", requestURI + params, "", headers)
        reply = connection.getresponse()

        body = reply.read()

        campaigns = rest_encoder.decode(body)
        return campaigns

    def search_paginated_recordings(self, campaign_id, key, page, pagesize):
        connection = RecordingConfig.getWSConnection()

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/" + \
                        str(campaign_id) + "/search"

        parameters = "?key=" + key + "&_page=" + page + "&_pagesize=" +\
                                             pagesize
        requestURI += parameters
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE
        connection.request("GET", requestURI, '', headers)
        reply = connection.getresponse()
        return rest_encoder.decode(reply.read())

    def delete_all_campaigns(self):
        campaign_db = _init_db_connection(RecordCampaignDbBinder)
        recording_db = _init_db_connection(RecordingDetailsDbBinder)
        recording_db.session.query(RecordingDetailsDao).delete()
        recording_db.session.commit()
        campaign_db.session.query(RecordCampaignDao).delete()
        campaign_db.session.commit()

    def list_all_recordings(self):
        recording_db = _init_db_connection(RecordingDetailsDbBinder)
        result = recording_db.session.query(RecordingDetailsDao).all()
        return table_list_to_list_dict(result)