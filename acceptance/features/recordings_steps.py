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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..

from lettuce import step
from rest_campaign import RestCampaign
from time import strftime, localtime
from xivo_recording.dao.record_campaign_dao import RecordCampaignDbBinder
from xivo_recording.recording_config import RecordingConfig
import random

#######################################################
# !!!!!!!!!!!!!!!!!!! TODO: delete random.randint!!!! #
#######################################################

rest_campaign = RestCampaign()
caller = '2222'
callee = '3333'
time = strftime("%a, %d %b %Y %H:%M:%S", localtime())
callid = None
campaign_name = None
queue_name = "test_queue" + str(random.randint(10, 99))
add_result = None


@step(u'Given there is no agent with number "([^"]*)"')
def given_there_is_no_agent_with_number_group1(step, agent_no):
    assert not rest_campaign.agent_exists(agent_no), 'Agent must not exist!'


@step(u'Then I get a response with error code \'([^\']*)\' and message \'([^\']*)\'')
def then_i_get_a_error_code_group1_with_message_group2(step, error_code, error_message):
    global add_result
    print "\nReceived code, message: " + str(add_result) + "\n"
    print "\nAwaited code, message: " + error_code + ", " + error_message + "\n"
    assert (str(add_result[0]) == error_code), 'Got wrong error code'
    assert (str(add_result[1]).strip() == error_message), 'Got wrong error message'


@step(u'Given there is a campaign named "([^"]*)"')
def given_there_is_a_campaign_named_campaing_name(step, local_campaign_name):
    global campaign_name
    campaign_name = local_campaign_name + str(random.randint(100, 999))
    assert rest_campaign.create(campaign_name), "Cannot create a campaign"


@step(u'Given there is an agent with number "([^"]*)"')
def given_there_is_an_agent_with_number_group1(step, agent_number):
    id = rest_campaign.add_agent_if_not_exists(agent_number)
    print "\n\t Received id: " + str(id) + "\n"
    assert (id > 0)


@step(u'When I save call details for a call referenced by its "([^"]*)" in campaign "([^"]*)" replied by agent with number "([^"]*)"')
def when_i_save_call_details_for_a_call_referenced_by_its_group1_in_campaign_group2_replied_by_agent_with_number_group3(step, local_callid, local_campaign_name, local_agent_no):
    global callid, campaign_name
    callid = local_callid + str(random.randint(1000, 9999))
    assert callid, "Callid null!"
    record_db = RecordCampaignDbBinder.new_from_uri(RecordingConfig.RECORDING_DB_URI)
    campaign_id = record_db.id_from_name(campaign_name)
    global add_result
    add_result = rest_campaign.addRecordingDetails(campaign_id, callid, caller, local_agent_no, time, queue_name)


@step(u'Then I can consult these details')
def then_i_can_consult_these_details(step):
    global add_result
    assert (add_result == (201, "Added: True")), 'Cannot add call details'

    global campaign_name, callid
    record_db = RecordCampaignDbBinder.new_from_uri(RecordingConfig.RECORDING_DB_URI)
    campaign_id = record_db.id_from_name(campaign_name)
    assert rest_campaign.verifyRecordingsDetails(campaign_id, callid), "Recording not found"


@step(u'Given there is a recording referenced by a "([^"]*)"')
def given_there_is_a_recording_referenced_by_a_group1(step, callid):
    record_db = RecordCampaignDbBinder.new_from_uri(RecordingConfig.RECORDING_DB_URI)
    global campaign_name
    campaign_id = record_db.id_from_name(campaign_name)
    add_result = rest_campaign.addRecordingDetails(campaign_id, callid, "caller", "", time, "queue_name")
    assert (add_result == (201, "Added: True")), 'Cannot add call details'


@step(u'When I delete a recording referenced by this "([^"]*)"')
def when_i_delete_a_recording_referenced_by_this_group1(step, callid):
    assert False, 'This step must be implemented'


@step(u'Then the recording is deleted and I get a response with code "([^"]*)"')
def then_the_recording_is_deleted_and_i_get_a_response_with_code_group1(step, response_code):
    assert False, 'This step must be implemented'
