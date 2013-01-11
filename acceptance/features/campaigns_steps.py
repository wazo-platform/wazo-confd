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

from acceptance.features.rest_queues import RestQueues
from lettuce import step
from rest_campaign import RestCampaign
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
def given_there_is_an_activated_campaign_named_group1_focusing_queue_group2(step, local_campaign_name, queue_id):
    global campaign_name
    r_queue = RestQueues()
    r_campaign = RestCampaign()
    r_queue.create_if_not_exists(queue_id)
    campaign_name = local_campaign_name + str(random.randint(100, 999))
    result = r_campaign.create(campaign_name, int(queue_id))
    assert result>0, "Cannot create campaign: " + campaign_name + " for queue: " + queue_id


@step(u'Given there is an non activated campaign named "([^"]*)" focusing queue "([^"]*)"')
def given_there_is_an_non_activated_campaign_named_group1_focusing_queue_group2(step, local_campaign_name, queue_id):
    r_queue = RestQueues()
    r_campaign = RestCampaign()
    r_queue.create_if_not_exists(queue_id)
    result = r_campaign.create(local_campaign_name + str(random.randint(100, 999)), int(queue_id))
    assert result > 0, "Cannot create campaign: " + local_campaign_name + " for queue: " + queue_id


activated_campaigns = None
@step(u'When I ask for activated campaigns for queue "([^"]*)"')
def when_i_ask_for_activated_campaigns_for_queue_group1(step, local_queue_id):
    global queue_id
    queue_id = local_queue_id
    r_campaign = RestCampaign()
    global activated_campaigns
    activated_campaigns = r_campaign.get_activated_campaigns(int(local_queue_id))['data']
    assert (activated_campaigns != None), "No activated campaign"


@step(u'Then I get a list of activated campaigns with campaign "([^"]*)"')
def then_i_get_a_list_of_activated_campaigns_with_campaign_group1(step, local_campaign_name):
    global activated_campaigns, queue_id, campaign_name
    result = False
    for campaign in activated_campaigns:
        if ((campaign['campaign_name'] == campaign_name) and
            (campaign['activated'] == 'True')):
            result = True
    assert result, 'Did not find campaign ' + campaign_name + ' in "' + \
        str(activated_campaigns) + \
        '") when asking for activated campaigns for queue: ' + \
        queue_id


#@step(u'Given I create a campaign "([^"]*)" pointing to queue "([^"]*)" with start date "([^"]*)" and end date "([^"]*)"')
#def edition_step_prerequisite(step, local_campaign_name, local_queue_id, local_start_date, local_end_date):
#    r_campaign = RestCampaign()
#    global campaign_id
#    new_campaign_name = local_campaign_name + str(random.randint(100, 999))
#    campaign_id = r_campaign.create(new_campaign_name, local_queue_id, True, local_start_date, local_end_date)
#    campaign = r_campaign.getCampaign(campaign_id)
#    assert campaign["campaign_name"] == new_campaign_name, 'Campaign ' + \
#                                    local_campaign_name + ' not properly inserted'


@step(u'When I change its name to "([^"]*)", its queue to "([^"]*)", its start date to "([^"]*)" and its end date to "([^"]*)"')
def edition_step_execution(step, local_campaign_name, local_queue_id, local_start_date, local_end_date):
    r_campaign = RestCampaign()
    global campaign_id, campaign_name, queue_id, start_date, end_date
    campaign_name = local_campaign_name + str(random.randint(100, 999))
    queue_id = local_queue_id
    start_date = local_start_date
    end_date = local_end_date
    params = {'campaign_name' : campaign_name,
              'queue_id' : queue_id,
              'start_date' : local_start_date,
              'end_date' : local_end_date
              }
    assert r_campaign.update(campaign_id, params), "Cannot update campaign " + str(campaign_id)


@step(u'Then the campaign is actually modified')
def then_the_campaign_is_actually_modified(step):
    r_campaign = RestCampaign()
    global campaign_id, campaign_name, queue_id, start_date, end_date
    campaign = r_campaign.getCampaign(campaign_id)
    assert campaign['campaign_name'] == campaign_name, "Name not properly modified"
    assert campaign['queue_id'] == queue_id, "Queue not properly modified"
    assert campaign['start_date'] == start_date, "Start date not properly modified"
    assert campaign['end_date'] == end_date, "End date not properly modified"


@step(u'Given there is a queue "([^"]*)" and a queue "([^"]*)"')
def given_there_is_a_queue_group1(step, queue_id1, queue_id2):
    r_queues = RestQueues()
    assert r_queues.list("id", queue_id1), "The queue of id " + queue_id1 + " does not exist."
    assert r_queues.list("id", queue_id2), "The queue of id " + queue_id2 + " does not exist."


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
def when_i_ask_for_running_and_activated_campaigns_for_queue_group1(step, queue_id):
    r_campaign = RestCampaign()
    global list_running_campaigns
    list_running_campaigns = r_campaign.getRunningActivatedCampaignsForQueue(queue_id)['data']
    assert len(list_running_campaigns) > 0, 'No campaign retrieved'


@step(u'Then I get campaign "([^"]*)", I do not get "([^"]*)", "([^"]*)", "([^"]*)"')
def then_i_get_campaign_group1_i_do_not_get_group2_group3_group4(step, group1, group2, group3, group4):
    global list_running_campaigns, running_scenario
    list_names = [item['campaign_name'] for item in list_running_campaigns]
    assert running_scenario[group1] in list_names, group1 + ' was not retrieved.'
    assert running_scenario[group2] not in list_names, group2 + ' was not retrieved.'
    assert running_scenario[group3] not in list_names, group3 + ' was not retrieved.'
    assert running_scenario[group4] not in list_names, group4 + ' was not retrieved.'


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


@step(u'When I ask for all the campaigns')
def when_i_ask_for_all_the_campaigns(step):
    r_campaign = RestCampaign()
    assert False, 'This step must be implemented'


@step(u'Then the displayed total is equal to the actual number of campaigns')
def then_the_displayed_total_is_equal_to_the_actual_number_of_campaigns(step):
    assert False, 'This step must be implemented'
    

@step(u'Then I get an error code \'([^\']*)\' with message \'([^\']*)\'')
def then_i_get_an_error_code_group1_with_message_group2(step, group1, group2):
    assert False, 'This step must be implemented'