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
import random

#######################################################
# !!!!!!!!!!!!!!!!!!! TODO: delete random.randint!!!! #
#######################################################
campaign_name = ''
new_campaign_name = ''
new_queue_id = ''

@step(u'When I create a campaign "([^"]*)"')
def when_i_create_a_campaign_named_campagne_name(step, campaign_name):
    r_campaign = RestCampaign()
    assert r_campaign.create(campaign_name + str(random.randint(100, 999))), "Cannot create a campaign"


@step(u'Then I can consult this campaign')
def then_i_can_consult_this_campaign(step):
    r_campaign = RestCampaign()
    r_campaign.create('test_consult_campaign' + str(random.randint(100, 999)))
    assert r_campaign.list(), "Cannot consult campaign list"


@step(u'Given there is an activated campaign named "([^"]*)" focusing queue "([^"]*)"')
def given_there_is_an_activated_campaign_named_group1_focusing_queue_group2(step, campaign_name, queue_id):
    r_queue = RestQueues()
    r_campaign = RestCampaign()
    r_queue.create_if_not_exists(queue_id)
    assert r_campaign.create(campaign_name + str(random.randint(100, 999)), int(queue_id)), "Cannot create campaign: " + campaign_name + " for queue: " + queue_id


@step(u'Given there is an non activated campaign named "([^"]*)" focusing queue "([^"]*)"')
def given_there_is_an_non_activated_campaign_named_group1_focusing_queue_group2(step, campaign_name, queue_id):
    r_queue = RestQueues()
    r_campaign = RestCampaign()
    r_queue.create_if_not_exists(queue_id)
    assert r_campaign.create(campaign_name + str(random.randint(100, 999)), int(queue_id)), "Cannot create campaign: " + campaign_name + " for queue: " + queue_id


activated_campaigns = None
@step(u'When I ask for activated campaigns for queue "([^"]*)"')
def when_i_ask_for_activated_campaigns_for_queue_group1(step, queue_id):
    r_campaign = RestCampaign()
    global activated_campaigns
    activated_campaigns = r_campaign.get_activated_campaigns(int(queue_id))
    assert (activated_campaigns != None), "No activated campaign"


@step(u'Then I get a list of activated campaigns with campaign "([^"]*)"')
def then_i_get_a_list_of_activated_campaigns_with_campaign_group1(step, queue_id):
    global activated_campaigns
    result = False
    for campaign in activated_campaigns:
        if ((campaign['queue_id'] == queue_id) and
            (campaign['activated'] == 'True')):
            result = True
    assert result, 'Got wrong campaign ("' + \
        str(activated_campaigns) + \
        '") when asking for activated campaigns for queue: ' + \
        queue_id

@step(u'Given there is a queue "([^"]*)" and a queue "([^"]*)"')
def given_there_is_a_queue_group1(step, queue_id1, queue_id2):
    r_queues = RestQueues()
    assert r_queues.list("id", queue_id1), "The queue of id " + queue_id1 + " does not exist."
    assert r_queues.list("id", queue_id2), "The queue of id " + queue_id2 + " does not exist."
   
@step(u'Given I create a campaign "([^"]*)" pointing to queue "([^"]*)"')
def given_i_create_a_campaign_group1_pointing_to_queue_group2(step, local_campaign_name, queue_id):
    r_campaign = RestCampaign()
    global campaign_name
    campaign_name = local_campaign_name + str(random.randint(100, 999))
    assert r_campaign.create(campaign_name, int(queue_id)), "Cannot create campaign: " + campaign_name + " for queue: " + queue_id
    
@step(u'When I change its name to "([^"]*)" and its queue to "([^"]*)"')
def when_i_change_its_name_to_group1_and_its_queue_to_group2(step, new_campaign_name_local, queue_id):
    r_campaign = RestCampaign()
    global campaign_name, new_campaign_name, new_queue_id
    new_campaign_name = new_campaign_name_local + str(random.randint(100, 999))
    new_queue_id = queue_id
    params = {'campaign_name' : new_campaign_name,
              'queue_id' : new_queue_id}
    assert r_campaign.update(campaign_name, params), "Cannot update campaign " + campaign_name
    
@step(u'Then I can get it by asking for its new name')
def then_i_can_get_it_by_asking_for_its_new_name(step):
    r_campaign = RestCampaign()
    global new_campaign_name, new_queue_id
    campaign = r_campaign.getCampaign(new_campaign_name)
    assert (campaign[0]['campaign_name'] == new_campaign_name and campaign[0]['queue_id'] == new_queue_id), "No activated campaign"