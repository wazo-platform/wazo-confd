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

from acceptance.features.steps.helpers.rest_campaign import RestCampaign
from lettuce import step
from time import strftime, localtime
from xivo_dao import record_campaigns_dao
import random

#######################################################
# !!!!!!!!!!!!!!!!!!! TODO: delete random.randint!!!! #
#######################################################

rest_campaign = RestCampaign()
caller = '2222'
callee = '3333'
time = strftime("%a, %d %b %Y %H:%M:%S", localtime())
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
    print "\nReceived code %s, message %s: " % (add_result.status, add_result.data) + "\n"
    print "\nAwaited code, message: " + error_code + ", " + error_message + "\n"
    assert (str(add_result.status) == error_code), 'Got wrong error code'
    assert (str(add_result.data).strip() == error_message), 'Got wrong error message: ' + add_result.data


@step(u'Given there is a campaign named "([^"]*)" for a queue "([^"]*)"')
def given_there_is_a_campaign_named_group1_for_a_queue_group2(step, campaign_name, local_queue_name):
    assert rest_campaign.create(campaign_name, local_queue_name), "Cannot create a campaign"


@step(u'Given there is an agent with number "([^"]*)"')
def given_there_is_an_agent_with_number_group1(step, agent_number):
    campaign_id = rest_campaign.add_agent_if_not_exists(agent_number)
    print "\n\t Received id: " + str(campaign_id) + "\n"
    assert (id > 0)


@step(u'When I save call details with the following parameters:')
def when_i_save_call_details_with_the_following_parameters(step):
    global add_result, callid_list
    callid_list = []
    for recording in step.hashes:
        callid_list.append(recording['callid'])
        campaign_id = record_campaigns_dao.id_from_name(recording['campaign_name'])
        data = dict(recording)
        data['campaign_id'] = campaign_id
        del data['campaign_name']
        data['time'] = time
        add_result = rest_campaign.addRecordingDetails(**data)


@step(u'Then I can consult the recording "([^"]*)" in campaign "([^"]*)"')
def then_i_can_consult_these_details(step, callid, campaign_name):
    global add_result
    assert (add_result.status == 201), 'Cannot add call details'
    assert (add_result.data == "Added: True"), 'Cannot add call details'
    campaign_id = record_campaigns_dao.id_from_name(campaign_name)
    assert rest_campaign.verifyRecordingsDetails(campaign_id, callid), "Recording not found"


@step(u'Given there is an agent of number "([^"]*)"')
def given_there_is_an_agent_of_number(step, agent_number):
    r_campaign = RestCampaign()
    result = r_campaign.add_agent_if_not_exists(agent_number)
    assert result > 0, 'The agent could not be created: ' + str(result)


@step(u'Given there are recordings with the following values:')
def given_there_are_recordings_with_the_following_values(step):
    str_step = 'When I save call details with the following parameters:\n' + \
               '| callid | campaign_name | agent_no | caller |\n'
    for recording in step.hashes:
        str_step += '| %s | %s | %s | %s |\n' % (recording['callid'],
                                                 recording['campaign_name'],
                                                 recording['agent_no'],
                                                 recording['caller'])
    step.behave_as(str_step)


@step(u'When I delete a recording referenced by this "([^"]*)" in campaign "([^"]*)"')
def when_i_delete_a_recording_referenced_by_this_callid(step, callid, campaign_name):
    global del_result
    campaign_id = record_campaigns_dao.id_from_name(campaign_name)
    del_result = rest_campaign.deleteRecording(campaign_id, callid)


@step(u'Then the recording is deleted and I get a response with code "([^"]*)"')
def then_the_recording_is_deleted_and_i_get_a_response_with_code_group1(step, response_code):
    global del_result
    assert del_result[0] == int(response_code), 'Wrong return status: ' + str(del_result)


@step(u'Given there is a campaign "([^"]*)"')
def given_there_is_a_campaign_group1(step, campaign_name):
    assert rest_campaign.create_if_not_exists(campaign_name), \
            'The campaign could not be created'


@step(u'Given there is an agent "([^"]*)"')
def given_there_is_an_agent(step, agent_no):
    agent_id = rest_campaign.add_agent_if_not_exists(agent_no)
    assert agent_id > 0, 'Could not create the agent'


@step(u'When I search recordings in the campaign "([^"]*)" with the key "([^"]*)"')
def when_i_search_recordings_in_the_campaign_with_the_key(step, campaign_name, key):
    global result
    campaign_id = record_campaigns_dao.id_from_name(campaign_name)
    result = rest_campaign.search_recordings(campaign_id, key)['items']
    assert len(result) > 0, 'No recording retrieved'


@step(u'Then I get the first two recordings')
def then_i_get_the_first_two_recordings(step):
    global result, callid_list
    liste = [item['cid'] for item in result]
    assert callid_list[0] in liste, "First call not in the list"
    assert callid_list[1] in liste, "Second call not in the list"
    assert callid_list[2] not in liste, "Third call in the list"


@step(u'Given there is no recording referenced by a "([^"]*)" in campaign "([^"]*)"')
def given_there_is_no_recording_referenced_by_a_group1_in_campaign_group2(step, callid, campaign_name):
    campaign_id = record_campaigns_dao.id_from_name(campaign_name)
    result = rest_campaign.verifyRecordingsDetails(campaign_id, callid)
    assert not result, 'The recording already exists'


@step(u'Then I get a response with error code \'([^\']*)\' with message \'([^\']*)\'')
def then_i_get_a_response_with_error_code_group1_with_message_group2(step, code, message):
    global del_result
    assert del_result == (int(code), message), "Got wrong response: " + str(del_result) + ", expected " + str((code, message))


@step(u'Given there are at least "([^"]*)" recordings for campaign "([^"]*)" and agent "([^"]*)"')
def given_there_are_at_least_group1_recordings_for_campaign_group2_and_agent_group3(step, nb_recordings, campaign_name, agent_no):
    campaign_id = record_campaigns_dao.id_from_name(campaign_name)
    res = rest_campaign.search_recordings(campaign_id, agent_no)
    print "\n==============res: ", res, "\n"
    if(res['total'] < int(nb_recordings)):
        i = res['total']
        while(i <= int(nb_recordings)):
            rest_campaign.addRecordingDetails(campaign_id, str(random.randint(1000, 9999)), "222", agent_no, time)
            i += 1
        res = rest_campaign.search_recordings(campaign_id, agent_no)
    assert res['total'] >= int(nb_recordings), 'Not enough recordings: ' + str(res)


@step(u'When I ask for the recordings of "([^"]*)"')
def when_i_ask_for_the_recordings_of_group1(step, campaign_name):
    global single_result
    campaign_id = record_campaigns_dao.id_from_name(campaign_name)
    single_result = rest_campaign.search_recordings(campaign_id)


@step(u'Then the displayed total is equal to the actual number of recordings')
def then_the_displayed_total_is_equal_to_the_actual_number_of_recordings(step):
    global single_result
    assert single_result['total'] == len(single_result['items']), 'Inconsistent number'


@step(u'When I ask for a list of recordings for "([^"]*)" with page "([^"]*)" and page size "([^"]*)"')
def when_i_ask_for_a_list_of_recordings_for_group1_with_page_group1_and_page_size_group3(step, campaign_name, page, pagesize):
    global single_result
    campaign_id = record_campaigns_dao.id_from_name(campaign_name)
    single_result = rest_campaign.paginated_recordings_list(str(campaign_id), page, pagesize)


@step(u'Then I get exactly "([^"]*)" recordings')
def then_i_get_exactly_group1_recordings(step, number):
    global single_result
    assert len(single_result['items']) == int(number), 'Inconsistent number retrieved: ' + str(single_result)


@step(u'Given I ask for a list of recordings for "([^"]*)" with page "([^"]*)" and page size "([^"]*)"')
def given_i_ask_for_a_list_of_recordings_for_group1_with_page_group1_and_page_size_group3(step, campaign, page, pagesize):
    global result_list
    result_list.append(rest_campaign.paginated_recordings_list(campaign, page, pagesize))


@step(u'Then the two lists of recording do not overlap')
def then_the_two_lists_of_recording_do_not_overlap(step):
    global result_list
    intersection = [item for item in result_list[0]['items'] if item in result_list[1]['items']]
    assert intersection == [], 'The results overlap: ' + str(intersection)


@step(u'When we search recordings in the campaign "([^"]*)" with the key "([^"]*)", page "([^"]*)" and page size "([^"]*)"')
def when_we_search_recordings_in_the_campaign_with_the_key_page_and_page_size(step, campaign_name, key, page, pagesize):
    global single_result
    campaign_id = record_campaigns_dao.id_from_name(campaign_name)
    single_result = rest_campaign.search_paginated_recordings(str(campaign_id), key, page, pagesize)


@step(u'Given there is a recording in campaign "([^"]*)" referenced by a "([^"]*)" answered by agent "([^"]*)"')
def given_there_is_a_recording_in_campaign_group1_referenced_by_a_group2_answered_by_agent_group3(step, campaign_name, callid, agent_no):
    campaign_id = record_campaigns_dao.id_from_name(campaign_name)
    time = "2012-01-01 00:00:00"
    assert rest_campaign.addRecordingDetails(campaign_id, callid, "caller",
                                             agent_no, time), "Impossible to create recording"
