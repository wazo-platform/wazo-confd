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
from xivo_restapi.dao.record_campaign_dao import RecordCampaignDbBinder, \
    RecordCampaignDao
from xivo_restapi.restapi_config import RestAPIConfig
import random
from xivo_restapi.services.manager_utils import _init_db_connection

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
result = []
callid_list = []
del_result = None
single_result = None
result_list = []


@step(u'Given there is no agent with number "([^"]*)"')
def given_there_is_no_agent_with_number_group1(step, agent_no):
    if rest_campaign.agent_exists(agent_no):
        assert rest_campaign.delete_agent(agent_no), "Could not delete the existing agent"
    else:
        assert True, "The agent does not exist"


@step(u'Given there is a queue named "([^"]*)"')
def given_there_is_a_queue_named_group1(step, queue_name):
    assert rest_campaign.queue_create_if_not_exists(queue_name), "Can't add queue"


@step(u'Then I get a response with error code \'([^\']*)\' and message \'([^\']*)\'')
def then_i_get_a_error_code_group1_with_message_group2(step, error_code, error_message):
    global add_result
    print "\nReceived code, message: " + str(add_result) + "\n"
    print "\nAwaited code, message: " + error_code + ", " + error_message + "\n"
    assert (str(add_result[0]) == error_code), 'Got wrong error code'
    assert (str(add_result[1]).strip() == error_message), 'Got wrong error message'


@step(u'Given there is a campaign named "([^"]*)" for a queue "([^"]*)"')
def given_there_is_a_campaign_named_group1_for_a_queue_group2(step, local_campaign_name, local_queue_name):
    global campaign_name
    campaign_name = local_campaign_name + str(random.randint(100, 999))
    assert rest_campaign.create(campaign_name, local_queue_name), "Cannot create a campaign"


@step(u'Given there is an agent with number "([^"]*)"')
def given_there_is_an_agent_with_number_group1(step, agent_number):
    campaign_id = rest_campaign.add_agent_if_not_exists(agent_number)
    print "\n\t Received id: " + str(campaign_id) + "\n"
    assert (id > 0)


@step(u'When I save call details for a call referenced by its "([^"]*)" in campaign "([^"]*)" replied by agent with number "([^"]*)"')
def when_i_save_call_details_for_a_call_referenced_by_its_group1_in_campaign_group2_replied_by_agent_with_number_group3(step, local_callid, local_campaign_name, local_agent_no):
    global callid, campaign_name
    callid = local_callid + str(random.randint(1000, 9999))
    assert callid, "Callid null!"
    record_db = RecordCampaignDbBinder.new_from_uri(RestAPIConfig.RECORDING_DB_URI)
    campaign_id = record_db.id_from_name(campaign_name)
    global add_result
    add_result = rest_campaign.addRecordingDetails(campaign_id, callid, caller, local_agent_no, time)


@step(u'Then I can consult these details')
def then_i_can_consult_these_details(step):
    global add_result
    assert (add_result == (201, "Added: True")), 'Cannot add call details'
    global campaign_name, callid
    record_db = RecordCampaignDbBinder.new_from_uri('asterisk')
    campaign_id = record_db.id_from_name(campaign_name)
    assert rest_campaign.verifyRecordingsDetails(campaign_id, callid), "Recording not found"


@step(u'Then I delete this recording and the agent "([^"]*)"')
def then_i_delete_this_recording_and_the_agent_group1(step, agent_no):
    global campaign_name, callid
    record_db = RecordCampaignDbBinder.new_from_uri('asterisk')
    campaign_id = record_db.id_from_name(campaign_name)
    res_rec = rest_campaign.deleteRecording(campaign_id, callid)
    assert res_rec[0] == 200, "Could not delete the recording: " + str(res_rec)
    assert rest_campaign.delete_agent(agent_no), "Could not delete the agent"


@step(u'Given there is an agent of number "([^"]*)"')
def given_there_is_an_agent_of_number(step, agent_number):
    r_campaign = RestCampaign()
    result = r_campaign.add_agent_if_not_exists(agent_number)
    assert result > 0, 'The agent could not be created: ' + str(result)


@step(u'Given there is a recording referenced by a "([^"]*)" with agent "([^"]*)"')
def given_there_is_a_recording_referenced_by_a_callid(step, local_callid, agent_no):
    #record_db = RecordCampaignDbBinder.new_from_uri(RestAPIConfig.RECORDING_DB_URI)
    record_db = RecordCampaignDbBinder.new_from_uri('asterisk')
    global campaign_name
    campaign_id = record_db.id_from_name(campaign_name)
    add_result = rest_campaign.addRecordingDetails(campaign_id, local_callid, "caller", agent_no, time)
    assert (add_result == (201, "Added: True")), 'Cannot add call details: ' + str(add_result)


@step(u'When I delete a recording referenced by this "([^"]*)"')
def when_i_delete_a_recording_referenced_by_this_callid(step, local_callid):
    global callid, campaign_name, del_result
    record_db = RecordCampaignDbBinder.new_from_uri('asterisk')
    campaign_id = record_db.id_from_name(campaign_name)
    del_result = rest_campaign.deleteRecording(campaign_id, local_callid)


@step(u'Then the recording is deleted and I get a response with code "([^"]*)"')
def then_the_recording_is_deleted_and_i_get_a_response_with_code_group1(step, response_code):
    global del_result
    assert del_result[0] == 200, 'Wrong return status: ' + str(del_result)


@step(u'Given there is a campaign of id "([^"]*)"')
def given_there_is_a_campaign_of_id(step, campaign_id):
    assert rest_campaign.create_if_not_exists(campaign_id), \
            'The campaign could not be created'


@step(u'Given there is an agent "([^"]*)"')
def given_there_is_an_agent(step, agent_no):
    agent_id = rest_campaign.add_agent_if_not_exists(agent_no)
    assert agent_id > 0, 'Could not create the agent'


@step(u'Given I create a recording for campaign "([^"]*)" with caller "([^"]*)" and agent "([^"]*)"')
def given_i_create_a_recording_for_campaign_with_caller_and_agent(step, campaign_id, caller_no, agent_no):
    callid = str(random.randint(1000, 9999))
    callid_list.append(callid)
    time = "2012-01-01 00:00:00"
    assert rest_campaign.addRecordingDetails(campaign_id, callid,
                                             caller_no, agent_no, time), \
            "Cannot add call details"


@step(u'When I search recordings in the campaign "([^"]*)" with the key "([^"]*)"')
def when_i_search_recordings_in_the_campaign_with_the_key(step, campaign_id, key):
    global result
    result = rest_campaign.search_recordings(campaign_id, key)['data']
    assert len(result) > 0, 'No recording retrieved'


@step(u'Then I get the first two recordings')
def then_i_get_the_first_two_recordings(step):
    global result, callid_list
    liste = [item['cid'] for item in result]
    assert callid_list[0] in liste, "First call not in the list"
    assert callid_list[1] in liste, "Second call not in the list"
    assert callid_list[2] not in liste, "Third call in the list"


@step(u'Given there is no recording referenced by a "([^"]*)" in campaign "([^"]*)"')
def given_there_is_no_recording_referenced_by_a_group1_in_campaign_group2(step, callid, local_campaign_name):
    global campaign_name
    record_db = RecordCampaignDbBinder.new_from_uri('asterisk')
    campaign_id = record_db.id_from_name(campaign_name)
    result = rest_campaign.verifyRecordingsDetails(campaign_id, callid)
    assert not result, 'The recording already exists'


@step(u'Then I get a response with error code \'([^\']*)\' with message \'([^\']*)\'')
def then_i_get_a_response_with_error_code_group1_with_message_group2(step, code, message):
    global del_result
    assert del_result == (int(code), message), "Got wrong response: " + str(del_result) + ", expected " + str((code, message))


@step(u'Given there are at least "([^"]*)" recordings for "([^"]*)" and agent "([^"]*)"')
def given_there_are_at_least_group1_recordings_for_group2_and_agent_group3(step, num_rec, campaign, agent):
    res = rest_campaign.search_recordings(campaign, agent)
    if(res['total'] < int(num_rec)):
        i = res['total']
        while(i <= int(num_rec)):
            rest_campaign.addRecordingDetails(campaign, str(random.randint(1000, 9999)), "222", agent, time)
            i += 1
        res = rest_campaign.search_recordings(campaign, agent)
    assert res['total'] >= int(num_rec), 'Not enough recordings: ' + str(res)


@step(u'When I ask for the recordings of "([^"]*)"')
def when_i_ask_for_the_recordings_of_group1(step, campaign):
    global single_result
    single_result = rest_campaign.search_recordings(campaign)


@step(u'Then the displayed total is equal to the actual number of recordings')
def then_the_displayed_total_is_equal_to_the_actual_number_of_recordings(step):
    global single_result
    assert single_result['total'] == len(single_result['data']), 'Inconsistent number'


@step(u'When I ask for a list of recordings for "([^"]*)" with page "([^"]*)" and page size "([^"]*)"')
def when_i_ask_for_a_list_of_recordings_for_group1_with_page_group1_and_page_size_group3(step, campaign, page, pagesize):
    global single_result
    single_result = rest_campaign.paginated_recordings_list(campaign, page, pagesize)


@step(u'Then I get exactly "([^"]*)" recordings')
def then_i_get_exactly_group1_recordings(step, number):
    global single_result
    assert len(single_result['data']) == int(number), 'Inconsistent number retrieved: ' + str(single_result)


@step(u'Given I ask for a list of recordings for "([^"]*)" with page "([^"]*)" and page size "([^"]*)"')
def given_i_ask_for_a_list_of_recordings_for_group1_with_page_group1_and_page_size_group3(step, campaign, page, pagesize):
    global result_list
    result_list.append(rest_campaign.paginated_recordings_list(campaign, page, pagesize))


@step(u'Then the two lists of recording do not overlap')
def then_the_two_lists_of_recording_do_not_overlap(step):
    global result_list
    intersection = [item for item in result_list[0]['data'] if item in result_list[1]['data']]
    assert intersection == [], 'The results overlap: ' + str(intersection)


@step(u'When we search recordings in the campaign "([^"]*)" with the key "([^"]*)", page "([^"]*)" and page size "([^"]*)"')
def when_we_search_recordings_in_the_campaign_with_the_key_page_and_page_size(step, campaign, key, page, pagesize):
    global single_result
    single_result = rest_campaign.search_paginated_recordings(campaign, key, page, pagesize)


@step(u'Given there is a recording in campaign "([^"]*)" referenced by a "([^"]*)" answered by agent "([^"]*)"')
def given_there_is_a_recording_in_campaign_group1_referenced_by_a_group2_answered_by_agent_group3(step, local_campaign_name, callid, agent_no):
    record_db = _init_db_connection(RecordCampaignDbBinder)
    global campaign_name
    campaign_id = record_db.id_from_name(campaign_name)
    time = "2012-01-01 00:00:00"
    assert rest_campaign.addRecordingDetails(campaign_id, callid, "caller",
                                             agent_no, time), "Impossible to create recording"


#@step(u'Given I update the recording referenced by a "([^"]*)" with end time "([^"]*)"')
#def given_i_update_the_recording_referenced_by_a_group1_with_end_time_group2(step, group1, group2):
#    assert False, 'This step must be implemented'
#
#
#@step(u'When I consult the recording referenced by a "([^"]*)"')
#def when_i_consult_the_recording_referenced_by_a_group1(step, group1):
#    assert False, 'This step must be implemented'
#
#
#@step(u'Then I get a recording with end time "([^"]*)"')
#def then_i_get_a_recording_with_end_time_group1(step, group1):
#    assert False, 'This step must be implemented'


#@step(u'Given I update the recording referenced by a "([^"]*)" with end time "([^"]*)"')
#def given_i_update_the_recording_referenced_by_a_group1_with_end_time_group2(step, callid, end_time):
#    assert rest_campaign.addRecordingDetails(campaign_id, callid,
#                                             caller_no, agent_no, time), "Impossible to update "
#    assert False, 'This step must be implemented'
#
#
#@step(u'When I consult the recording referenced by a "([^"]*)"')
#def when_i_consult_the_recording_referenced_by_a_group1(step, group1):
#    assert False, 'This step must be implemented'
#
#
#@step(u'Then I get a recording with end time "([^"]*)"')
#def then_i_get_a_recording_with_end_time_group1(step, group1):
#    assert False, 'This step must be implemented'

