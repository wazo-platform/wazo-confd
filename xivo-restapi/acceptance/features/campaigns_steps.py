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
from xivo_dao import queue_dao, record_campaigns_dao
import datetime
import random

#######################################################
# !!!!!!!!!!!!!!!!!!! TODO: delete random.randint!!!! #
#######################################################
campaign_name = ''
new_campaign_name = ''
queue_id = ''
new_queue_id = ''
campaign_id = ''
running_scenario = {}
list_running_campaigns = []
start_date = ''
end_date = ''
return_tuple = None
result = None
result_list = []


@step(u'Given there is no campaign')
def given_there_is_no_campaign(step):
    r_campaign = RestCampaign()
    r_campaign.delete_all_campaigns()


@step(u'When I create a campaign "([^"]*)"')
def when_i_create_a_campaign_named_campagne_name(step, local_campaign_name):
    r_campaign = RestCampaign()
    global campaign_name
    campaign_name = local_campaign_name + str(random.randint(100, 999))
    result = r_campaign.create(campaign_name)
    assert result > 0, "Cannot create a campaign"


@step(u'Then I can consult this campaign')
def then_i_can_consult_this_campaign(step):
    r_campaign = RestCampaign()
    global campaign_name
    liste = [item["campaign_name"] for item in r_campaign.list()['data']]
    assert campaign_name in liste, campaign_name + " not in " + str(liste)


@step(u'Given there is an activated campaign named "([^"]*)" focusing queue "([^"]*)"')
def given_there_is_an_activated_campaign_named_group1_focusing_queue_group2(step, local_campaign_name, queue_name):
    global campaign_name
    r_campaign = RestCampaign()
    campaign_name = local_campaign_name + str(random.randint(100, 999))
    result = r_campaign.create(campaign_name, queue_name)
    assert result > 0, "Cannot create campaign: " + campaign_name + " for queue: " + queue_name


@step(u'Given there is an non activated campaign named "([^"]*)" focusing queue "([^"]*)"')
def given_there_is_an_non_activated_campaign_named_group1_focusing_queue_group2(step, local_campaign_name, queue_name):
    r_campaign = RestCampaign()
    r_campaign.queue_create_if_not_exists(queue_name)
    result = r_campaign.create(local_campaign_name + str(random.randint(100, 999)), queue_name)
    assert result > 0, "Cannot create campaign: " + local_campaign_name + " for queue: " + queue_name


activated_campaigns = None


@step(u'When I ask for activated campaigns for queue "([^"]*)"')
def when_i_ask_for_activated_campaigns_for_queue_group1(step, queue_name):
    global queue_id
    queue_id = queue_dao.id_from_name(queue_name)
    r_campaign = RestCampaign()
    global activated_campaigns
    activated_campaigns = r_campaign.get_activated_campaigns(queue_id)['data']
    assert (activated_campaigns != None), "No activated campaign"


@step(u'Then I get a list of activated campaigns with campaign "([^"]*)"')
def then_i_get_a_list_of_activated_campaigns_with_campaign_group1(step, local_campaign_name):
    global activated_campaigns, queue_id, campaign_name
    result = False
    for campaign in activated_campaigns:
        if ((campaign['campaign_name'] == campaign_name) and campaign['activated']):
            result = True
            break
    assert result, 'Did not find campaign ' + campaign_name + ' in "' + \
        str(activated_campaigns) + \
        '") when asking for activated campaigns for queue: ' + \
        str(queue_id)


@step(u'Given I create a campaign "([^"]*)" pointing to queue "([^"]*)" with start date "([^"]*)" and end date "([^"]*)"')
def edition_step_prerequisite(step, local_campaign_name, queue_name, local_start_date, local_end_date):
    r_campaign = RestCampaign()
    global campaign_id
    campaign_id = r_campaign.create(local_campaign_name, queue_name, True, local_start_date, local_end_date)
    campaign = r_campaign.getCampaign(campaign_id)
    assert campaign["campaign_name"] == local_campaign_name, 'Campaign ' + \
                                    local_campaign_name + ' not properly inserted'


@step(u'When I change its name to "([^"]*)", its queue to "([^"]*)", its start date to "([^"]*)" and its end date to "([^"]*)"')
def edition_step_execution(step, local_campaign_name, queue_name, local_start_date, local_end_date):
    r_campaign = RestCampaign()
    global campaign_id, campaign_name, queue_id, start_date, end_date
    campaign_name = local_campaign_name + str(random.randint(100, 999))
    queue_id = str(queue_dao.id_from_name(queue_name))
    start_date = local_start_date
    end_date = local_end_date
    params = {'campaign_name': campaign_name,
              'queue_id': queue_id,
              'start_date': local_start_date,
              'end_date': local_end_date
              }
    assert r_campaign.updateCampaign(campaign_id, params), "Cannot update campaign " + str(campaign_id)


@step(u'Then the campaign is actually modified')
def then_the_campaign_is_actually_modified(step):
    r_campaign = RestCampaign()
    global campaign_id, campaign_name, queue_id, start_date, end_date
    campaign = r_campaign.getCampaign(campaign_id)
    assert campaign['campaign_name'] == campaign_name, "Name not properly modified"
    assert campaign['queue_id'] == int(queue_id), "Queue not properly modified"
    assert campaign['start_date'] == start_date, "Start date not properly modified"
    assert campaign['end_date'] == end_date, "End date not properly modified"


@step(u'Given there is a queue "([^"]*)" and a queue "([^"]*)"')
def given_there_is_a_queue_group1(step, queue1, queue2):
    r_campaign = RestCampaign()
    r_campaign.queue_create_if_not_exists(queue1)
    r_campaign.queue_create_if_not_exists(queue2)


@step(u'Given I create an activated campaign "([^"]*)" pointing to queue "([^"]*)" currently running')
def given_i_create_an_activated_campaign_group1_pointing_to_queue_group2_currently_running(step, campaign_name, queue_id):
    r_campaign = RestCampaign()
    global running_scenario
    now = datetime.datetime.now()
    new_campaign_name = campaign_name + str(random.randint(100, 999))
    running_scenario[campaign_name] = new_campaign_name
    d = datetime.timedelta(days=1)
    gen_id = r_campaign.create(new_campaign_name, queue_id, True, (now - d).strftime("%Y-%m-%d"),
                                                                (now + d).strftime("%Y-%m-%d"))
    assert r_campaign.getCampaign(gen_id)["campaign_name"] == new_campaign_name, 'Campaign ' + \
                                    campaign_name + ' not properly inserted'


@step(u'Given I create a non activated campaign "([^"]*)" pointing to queue "([^"]*)" currently running')
def given_i_create_a_non_activated_campaign_group1_pointing_to_queue_group2_currently_running(step, campaign_name, queue_id):
    r_campaign = RestCampaign()
    global running_scenario
    now = datetime.datetime.now()
    new_campaign_name = campaign_name + str(random.randint(100, 999))
    running_scenario[campaign_name] = new_campaign_name
    d = datetime.timedelta(days=1)
    gen_id = r_campaign.create(new_campaign_name, queue_id, False, (now - d).strftime("%Y-%m-%d"),
                               (now + d).strftime("%Y-%m-%d"))
    assert r_campaign.getCampaign(gen_id)["campaign_name"] == new_campaign_name, 'Campaign ' + \
                                    campaign_name + ' not properly inserted'


@step(u'Given I create an activated campaign "([^"]*)" pointing to queue "([^"]*)" currently not running')
def given_i_create_an_activated_campaign_group1_pointing_to_queue_group2_currently_not_running(step, campaign_name, queue_id):
    r_campaign = RestCampaign()
    global running_scenario
    now = datetime.datetime.now()
    new_campaign_name = campaign_name + str(random.randint(100, 999))
    running_scenario[campaign_name] = new_campaign_name
    d = datetime.timedelta(days=1)
    gen_id = r_campaign.create(new_campaign_name, queue_id, True, (now + d).strftime("%Y-%m-%d"),
                               (now + 2 * d).strftime("%Y-%m-%d"))
    assert r_campaign.getCampaign(gen_id)["campaign_name"] == new_campaign_name, 'Campaign ' + \
                                    campaign_name + ' not properly inserted'


@step(u'When I ask for running and activated campaigns for queue "([^"]*)"')
def when_i_ask_for_running_and_activated_campaigns_for_queue_group1(step, queue_name):
    r_campaign = RestCampaign()
    global list_running_campaigns
    queue_id = queue_dao.id_from_name(queue_name)
    list_running_campaigns = r_campaign.getRunningActivatedCampaignsForQueue(str(queue_id))['data']
    assert len(list_running_campaigns) > 0, 'No campaign retrieved'


@step(u'Then I get campaign "([^"]*)", I do not get "([^"]*)", "([^"]*)"')
def then_i_get_campaign_group1_i_do_not_get_group2_group3_group4(step, group1, group2, group3):
    global list_running_campaigns, running_scenario
    list_names = [item['campaign_name'] for item in list_running_campaigns]
    assert running_scenario[group1] in list_names, group1 + ' was not retrieved.'
    assert running_scenario[group2] not in list_names, group2 + ' was not retrieved.'
    assert running_scenario[group3] not in list_names, group3 + ' was not retrieved.'


@step(u'Then this campaign is created with its start date and end date equal to now')
def then_this_campaign_is_created_with_its_start_date_and_end_date_equal_to_now(step):
    r_campaign = RestCampaign()
    global campaign_name
    liste = r_campaign.list()['data']
    result = False
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    for item in liste:
        if(item["campaign_name"] == campaign_name and \
           item["start_date"][:10] == now and item["end_date"][:10] == now):
            result = True
    assert result, 'Campaign not created with the current date: '


@step(u'When I create the campaign "([^"]*)" with start date "([^"]*)" and end date "([^"]*)"')
def step_unproper_dates(step, campaign, sdate, edate):
    r_campaign = RestCampaign()
    global return_tuple
    return_tuple = r_campaign.create_with_errors(campaign, 'test', True, sdate,
                               edate)


@step(u'Then I get an error code \'([^\']*)\' with message \'([^\']*)\'')
def then_i_get_an_error_code_group1_with_message_group2(step, error_code, message):
    global return_tuple
    assert str(return_tuple[0]) == error_code, "Got wrong error code: " + str(return_tuple[0])
    assert return_tuple[1] == [message], "Got wrong message: " + str(return_tuple[1])


@step(u'When I ask for all the campaigns')
def when_i_ask_for_all_the_campaigns(step):
    r_campaign = RestCampaign()
    global result
    result = r_campaign.list()


@step(u'Then the displayed total is equal to the actual number of campaigns')
def then_the_displayed_total_is_equal_to_the_actual_number_of_campaigns(step):
    global result
    assert result['total'] == len(result['data']), 'Got total ' + str(result['total']) + \
        " but real number was " + str(len(result['data']))


@step(u'Given there are at least "([^"]*)" campaigns')
def given_there_are_at_least_group1_campaigns(step, num_of_campaigns):
    r_campaign = RestCampaign()
    res = r_campaign.list()
    if(res['total'] < int(num_of_campaigns)):
        i = res['total']
        now = datetime.datetime.now()
        while(i < int(num_of_campaigns)):
            d = datetime.timedelta(days=(i + 1))
            oned = datetime.timedelta(days=1)
            r_campaign.create(str(random.randint(1000, 9999)), 'test', True,
                              (now + d).strftime("%Y-%m-%d"), (now + d + oned).strftime("%Y-%m-%d"))
            i += 1
        res = r_campaign.list()
    assert res['total'] >= int(num_of_campaigns), 'Not enough campaigns: ' + str(res)


@step(u'When I ask for a list of campaigns with page "([^"]*)" and page size "([^"]*)"')
def when_i_ask_for_a_list_of_campaigns_with_page_group1_and_page_size_group2(step, page_number, page_size):
    r_campaign = RestCampaign()
    global result
    result = r_campaign.paginated_list(int(page_number), int(page_size))


@step(u'Then I get exactly "([^"]*)" campaigns')
def then_i_get_exactly_group1_campaigns(step, num_of_campaigns):
    global result
    assert len(result['data']) == int(num_of_campaigns), "Got wrong number of campaigns: " + str(result)


@step(u'Given I ask for a list of campaigns with page "([^"]*)" and page size "([^"]*)"')
def given_i_ask_for_a_list_of_campaigns_with_page_group1_and_page_size_group2(step, page_number, page_size):
    r_campaign = RestCampaign()
    global result_list
    result_list.append(r_campaign.paginated_list(int(page_number), int(page_size)))


@step(u'Then the two results do not overlap')
def then_the_two_results_do_not_overlap(step):
    global result_list
    intersection = [item for item in result_list[0]['data'] if item in result_list[1]['data']]
    assert intersection == [], 'The results overlap: ' + str(intersection)


@step(u'When I try to create a campaign "([^"]*)" pointing to queue "([^"]*)" with start date "([^"]*)" and end date "([^"]*)"')
def when_i_try_to_create_a_campaign_group1_pointing_to_queue_group2_with_start_date_group3_and_end_date_group4(step, name, queue, start, end):
    r_campaign = RestCampaign()
    global return_tuple
    return_tuple = r_campaign.create_with_errors(name, queue, True, start, end)


@step(u'When I delete the queue "([^"]*)"')
def when_i_delete_the_queue_group1(step, queue_name):
    r_campaign = RestCampaign()
    r_campaign.delete_queue(queue_name)


@step(u'Then the queue "([^"]*)" is actually deleted')
def then_the_queue_group1_is_actually_deleted(step, queue_name):
    r_campaign = RestCampaign()
    result = r_campaign.get_queue(queue_name)
    assert result == None


@step(u'Then I can get the campaign "([^"]*)" with an empty queue_id')
def then_i_can_get_the_campaign_group1_has_an_empty_queue_id(step, campaign_name):
    r_campaign = RestCampaign()
    global campaign_id
    result = r_campaign.getCampaign(campaign_id)
    assert result != None, "No campaign retrieved"
    assert result['queue_id'] is None, "queue_id not null"


@step(u'Given there is at least one recording for the campaign "([^"]*)"')
def given_there_s_at_least_one_recording_for_the_campaign_group1(step, group1):
    global campaign_id
    r_campaign = RestCampaign()
    agent_no = '4000'
    r_campaign.add_agent_if_not_exists(agent_no)
    callid = str(random.randint(1000, 9999))
    time = strftime("%a, %d %b %Y %H:%M:%S", localtime())
    r_campaign.addRecordingDetails(campaign_id, callid, '2002', agent_no, time)


@step(u'When I ask to delete the campaign "([^"]*)"')
def when_i_ask_to_delete_the_campaign_group1(step, group1):
    global campaign_id, return_tuple
    r_campaign = RestCampaign()
    result = r_campaign.delete_campaign(campaign_id)
    return_tuple = (result.status, result.data)


@step(u'Given there is not any recording for the campaign "([^"]*)"')
def given_there_isn_t_any_recording_for_the_campaign_group1(step, campaign_name):
    r_campaign = RestCampaign()
    r_campaign.delete_recordings(campaign_name)


@step(u'Then I get a response with code \'([^\']*)\' and the campaign is deleted')
def then_i_get_a_response_with_code_group1_and_the_campaign_is_deleted(step, code):
    global return_tuple, campaign_id
    assert str(return_tuple[0]) == code
    assert record_campaigns_dao.get(campaign_id) == None
