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
from xivo_dao import queue_dao, record_campaigns_dao, recordings_dao
import datetime

callid = '1'
campaign_id = ''
list_running_campaigns = []
return_tuple = None
result = None
result_list = []
r_campaign = RestCampaign()

@step(u'Given there is no campaign')
def given_there_is_no_campaign(step):
    r_campaign.delete_all_campaigns()


@step(u'When I create a campaign "([^"]*)"')
def when_i_create_a_campaign_named_campagne_name(step, campaign_name):
    result = r_campaign.create(campaign_name)
    assert result > 0, "Cannot create a campaign"


@step(u'Then I can consult the campaign named "([^"]*)"')
def then_i_can_consult_the_campaign_named_group1(step, campaign_name):
    liste = [item["campaign_name"] for item in r_campaign.list()['items']]
    assert campaign_name in liste, "%s not in %s" % (campaign_name, liste)


@step(u'Given there is an activated campaign named "([^"]*)" focusing queue "([^"]*)"')
def given_there_is_an_activated_campaign_named_group1_focusing_queue_group2(step, campaign_name, queue_name):
    result = r_campaign.create(campaign_name, queue_name)
    assert result > 0, "Cannot create campaign: " + campaign_name + " for queue: " + queue_name


@step(u'Given there is an non activated campaign named "([^"]*)" focusing queue "([^"]*)"')
def given_there_is_an_non_activated_campaign_named_group1_focusing_queue_group2(step, campaign_name, queue_name):
    r_campaign.queue_create_if_not_exists(queue_name)
    result = r_campaign.create(campaign_name, queue_name)
    assert result > 0, "Cannot create campaign: " + campaign_name + " for queue: " + queue_name


activated_campaigns = None


@step(u'When I ask for activated campaigns for queue "([^"]*)"')
def when_i_ask_for_activated_campaigns_for_queue_group1(step, queue_name):
    global activated_campaigns
    queue_id = queue_dao.id_from_name(queue_name)
    activated_campaigns = r_campaign.get_activated_campaigns(queue_id)['items']
    assert (activated_campaigns != None), "No activated campaign"


@step(u'Then I get a list of activated campaigns with campaign "([^"]*)"')
def then_i_get_a_list_of_activated_campaigns_with_campaign_group1(step, campaign_name):
    global activated_campaigns
    result = False
    for campaign in activated_campaigns:
        if ((campaign['campaign_name'] == campaign_name) and campaign['activated']):
            result = True
            break
    assert result, 'Did not find campaign ' + campaign_name + ' in "' + \
        str(activated_campaigns)


@step(u'Given I create a campaign with the following parameters:')
def given_i_create_a_campaign_with_the_following_parameters(step):
    global campaign_id, return_tuple
    campaign = dict(step.hashes[0])
    if (campaign['queue_name'] == ''):
        del campaign['queue_name']
    #print "campaign: queue_name: ", campaign['queue_name']
    reply = r_campaign.create(**campaign)
    campaign_id = reply.data
    return_tuple = reply.status, reply.data


@step(u'When I edit it with the following parameters:')
def when_i_edit_it_with_the_following_parameters(step):
    global campaign_id
    campaign = step.hashes[0]
    params = dict(campaign)
    params['queue_id'] = queue_dao.id_from_name(campaign['queue_name'])
    del params['queue_name']
    assert r_campaign.updateCampaign(campaign_id, params), "Cannot update campaign " + str(campaign_id)


@step(u'Then the campaign is actually modified with the following values:')
def then_the_campaign_is_actually_modified_with_the_following_values(step):
    global campaign_id
    campaign = r_campaign.getCampaign(campaign_id)
    expected_campaign = step.hashes[0]
    queue_id = queue_dao.id_from_name(expected_campaign['queue_name'])
    assert campaign['campaign_name'] == expected_campaign['campaign_name']
    assert campaign['queue_id'] == queue_id
    assert campaign['start_date'] == expected_campaign['start_date']
    assert campaign['end_date'] == expected_campaign['end_date']


@step(u'Given there is a queue "([^"]*)" and a queue "([^"]*)"')
def given_there_is_a_queue_group1(step, queue1, queue2):
    r_campaign.queue_create_if_not_exists(queue1)
    r_campaign.queue_create_if_not_exists(queue2)


@step(u'Given I create an activated campaign "([^"]*)" pointing to queue "([^"]*)" currently running')
def given_i_create_an_activated_campaign_group1_pointing_to_queue_group2_currently_running(step, campaign_name, queue_id):
    now = datetime.datetime.now()
    d = datetime.timedelta(days=1)
    gen_id = r_campaign.create(campaign_name, queue_id, True, (now - d).strftime("%Y-%m-%d"),
                                                                (now + d).strftime("%Y-%m-%d")).data
    assert r_campaign.getCampaign(gen_id)["campaign_name"] == campaign_name, 'Campaign ' + \
                                    campaign_name + ' not properly inserted'


@step(u'Given I create a non activated campaign "([^"]*)" pointing to queue "([^"]*)" currently running')
def given_i_create_a_non_activated_campaign_group1_pointing_to_queue_group2_currently_running(step, campaign_name, queue_id):
    now = datetime.datetime.now()
    d = datetime.timedelta(days=1)
    gen_id = r_campaign.create(campaign_name, queue_id, False, (now - d).strftime("%Y-%m-%d"),
                               (now + d).strftime("%Y-%m-%d")).data
    assert r_campaign.getCampaign(gen_id)["campaign_name"] == campaign_name, 'Campaign ' + \
                                    campaign_name + ' not properly inserted'


@step(u'Given I create an activated campaign "([^"]*)" pointing to queue "([^"]*)" currently not running')
def given_i_create_an_activated_campaign_group1_pointing_to_queue_group2_currently_not_running(step, campaign_name, queue_id):
    now = datetime.datetime.now()
    d = datetime.timedelta(days=1)
    gen_id = r_campaign.create(campaign_name, queue_id, True, (now + d).strftime("%Y-%m-%d"),
                               (now + 2 * d).strftime("%Y-%m-%d")).data
    assert r_campaign.getCampaign(gen_id)["campaign_name"] == campaign_name, 'Campaign ' + \
                                    campaign_name + ' not properly inserted'


@step(u'When I ask for running and activated campaigns for queue "([^"]*)"')
def when_i_ask_for_running_and_activated_campaigns_for_queue_group1(step, queue_name):
    global list_running_campaigns
    queue_id = queue_dao.id_from_name(queue_name)
    list_running_campaigns = r_campaign.getRunningActivatedCampaignsForQueue(str(queue_id))['items']
    assert len(list_running_campaigns) > 0, 'No campaign retrieved'


@step(u'Then I get campaign "([^"]*)", I do not get "([^"]*)", "([^"]*)"')
def then_i_get_campaign_group1_i_do_not_get_group2_group3_group4(step, campaign1, campaign2, campaign3):
    global list_running_campaigns
    list_names = [item['campaign_name'] for item in list_running_campaigns]
    assert campaign1 in list_names, campaign1 + ' was not retrieved.'
    assert campaign2 not in list_names, campaign2 + ' was not retrieved.'
    assert campaign3 not in list_names, campaign3 + ' was not retrieved.'


@step(u'Then the campaign "([^"]*)" is created with its start date and end date equal to now')
def then_the_campaign_group1_is_created_with_its_start_date_and_end_date_equal_to_now(step, campaign_name):
    liste = r_campaign.list()['items']
    result = False
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    for item in liste:
        if(item["campaign_name"] == campaign_name and \
           item["start_date"][:10] == now and item["end_date"][:10] == now):
            result = True
    assert result, 'Campaign not created with the current date: '

@step(u'When I create a campaign with the following parameters:')
def when_i_create_a_campaign_with_the_following_parameters(step):
    #import pdb; pdb.set_trace()
    step.behave_as('Given I create a campaign with the following parameters:\n' +
                   '| campaign_name | queue_name | start_date | end_date |\n' +
                   '| %s | %s | %s | %s |' % tuple(step.hashes[0].values()))


@step(u'Then I get an error code "([^\']*)" with message "([^\']*)"')
def then_i_get_an_error_code_group1_with_message_group2(step, error_code, message):
    global return_tuple
    assert str(return_tuple[0]) == error_code, "Got wrong error code: " + str(return_tuple[0])
    assert return_tuple[1] == [message], "Got wrong message: " + str(return_tuple[1])


@step(u'When I ask for all the campaigns')
def when_i_ask_for_all_the_campaigns(step):
    global result
    result = r_campaign.list()


@step(u'Then the displayed total is equal to the actual number of campaigns')
def then_the_displayed_total_is_equal_to_the_actual_number_of_campaigns(step):
    global result
    assert result['total'] == len(result['items']), 'Got total ' + str(result['total']) + \
        " but real number was " + str(len(result['items']))


@step(u'Given there are at least "([^"]*)" campaigns')
def given_there_are_at_least_group1_campaigns(step, num_of_campaigns):
    res = r_campaign.list()
    if(res['total'] < int(num_of_campaigns)):
        i = res['total']
        now = datetime.datetime.now()
        while(i <= int(num_of_campaigns)):
            d = datetime.timedelta(days=(i + 1))
            oned = datetime.timedelta(days=1)
            r_campaign.create('campaign_%d' % i, 'test', True,
                              (now + d).strftime("%Y-%m-%d"), (now + d + oned).strftime("%Y-%m-%d"))
            i += 1
        res = r_campaign.list()
    assert res['total'] >= int(num_of_campaigns), 'Not enough campaigns: ' + str(res)


@step(u'When I ask for a list of campaigns with page "([^"]*)" and page size "([^"]*)"')
def when_i_ask_for_a_list_of_campaigns_with_page_group1_and_page_size_group2(step, page_number, page_size):
    global result
    result = r_campaign.paginated_list(int(page_number), int(page_size))


@step(u'Then I get exactly "([^"]*)" campaigns')
def then_i_get_exactly_group1_campaigns(step, num_of_campaigns):
    global result
    assert len(result['items']) == int(num_of_campaigns), "Got wrong number of campaigns: " + str(result)


@step(u'Given I ask for a list of campaigns with page "([^"]*)" and page size "([^"]*)"')
def given_i_ask_for_a_list_of_campaigns_with_page_group1_and_page_size_group2(step, page_number, page_size):
    global result_list
    result_list.append(r_campaign.paginated_list(int(page_number), int(page_size)))


@step(u'Then the two results do not overlap')
def then_the_two_results_do_not_overlap(step):
    global result_list
    intersection = [item for item in result_list[0]['items'] if item in result_list[1]['items']]
    assert intersection == [], 'The results overlap: ' + str(intersection)


@step(u'When I try to create a campaign "([^"]*)" pointing to queue "([^"]*)" with start date "([^"]*)" and end date "([^"]*)"')
def when_i_try_to_create_a_campaign_group1_pointing_to_queue_group2_with_start_date_group3_and_end_date_group4(step, name, queue, start, end):
    global return_tuple
    return_tuple = r_campaign.create_with_errors(name, queue, True, start, end)


@step(u'When I delete the queue "([^"]*)"')
def when_i_delete_the_queue_group1(step, queue_name):
    queue_dao.delete_by_name(queue_name)


@step(u'Then the queue "([^"]*)" is actually deleted')
def then_the_queue_group1_is_actually_deleted(step, queue_name):
    gotException = False
    try:
        r_campaign.get_queue(queue_name)
    except LookupError:
        gotException = True
    assert gotException


@step(u'Then I can get the campaign "([^"]*)" with an empty queue_id')
def then_i_can_get_the_campaign_group1_with_an_empty_queue_id(step, campaign_name):
    campaign_id = record_campaigns_dao.id_from_name(campaign_name)
    result = r_campaign.getCampaign(campaign_id)
    assert result != None, "No campaign retrieved"
    assert result['queue_id'] is None, "queue_id not null"


@step(u'Given there is at least one recording for the campaign "([^"]*)"')
def given_there_s_at_least_one_recording_for_the_campaign_group1(step, campaign_name):
    global callid
    campaign_id = record_campaigns_dao.id_from_name(campaign_name)
    agent_no = '4000'
    r_campaign.add_agent_if_not_exists(agent_no)
    callid += '1'
    time = strftime("%a, %d %b %Y %H:%M:%S", localtime())
    r_campaign.addRecordingDetails(campaign_id, callid, '2002', agent_no, time)


@step(u'When I ask to delete the campaign "([^"]*)"')
def when_i_ask_to_delete_the_campaign_group1(step, campaign_name):
    global return_tuple
    campaign_id = record_campaigns_dao.id_from_name(campaign_name)
    result = r_campaign.delete_campaign(campaign_id)
    return_tuple = (result.status, result.data)


@step(u'Given there is not any recording for the campaign "([^"]*)"')
def given_there_isn_t_any_recording_for_the_campaign_group1(step, campaign_name):
    recordings_dao.delete_by_campaign_name(campaign_name)


@step(u'Then I get a response with code "([^\']*)" and the campaign is deleted')
def then_i_get_a_response_with_code_group1_and_the_campaign_is_deleted(step, code):
    global return_tuple, campaign_id
    assert str(return_tuple[0]) == code
    assert record_campaigns_dao.get(campaign_id) == None
