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
import random

#######################################################
# !!!!!!!!!!!!!!!!!!! TODO: delete random.randint!!!! #
#######################################################


@step(u'When I create a campaign named "([^"]*)"')
def when_i_create_a_campaign_named_campagne_name(step, campaign_name):
    r_campaign = RestCampaign()
    assert r_campaign.create(campaign_name + str(random.randint(100, 999))), "Cannot create a campaign"


@step(u'Then I can consult this campaign')
def then_i_can_consult_this_campaign(step):
    r_campaign = RestCampaign()
    r_campaign.create('test_consult_campaign' + str(random.randint(100, 999)))
    assert r_campaign.list(), "Cannot consult campaign list"


@step(u'Given there is an activated campaign named "([^"]*)" focusing queue "([^"]*)"')
def given_there_is_an_activated_campaign_named_group1_focusing_queue_group2(step, campaign_name, queue_name):
    r_campaign = RestCampaign()
    assert r_campaign.create(campaign_name + str(random.randint(100, 999)), queue_name), "Cannot create campaign: " + campaign_name + " for queue: " + queue_name


@step(u'Given there is an non activated campaign named "([^"]*)" focusing queue "([^"]*)"')
def given_there_is_an_non_activated_campaign_named_group1_focusing_queue_group2(step, campaign_name, queue_name):
    r_campaign = RestCampaign()
    assert r_campaign.create(campaign_name + str(random.randint(100, 999)), queue_name), "Cannot create campaign: " + campaign_name + " for queue: " + queue_name


activated_campaigns = None
@step(u'When I ask for activated campaigns for queue "([^"]*)"')
def when_i_ask_for_activated_campaigns_for_queue_group1(step, queue_name):
    r_campaign = RestCampaign()
    global activated_campaigns
    activated_campaigns = r_campaign.get_activated_campaigns(queue_name)
    assert (activated_campaigns != None), "No activated campaign"


@step(u'Then I get a list of activated campaigns with campaign "([^"]*)"')
def then_i_get_a_list_of_activated_campaigns_with_campaign_group1(step, queue_name):
    global activated_campaigns
    result = False
    for campaign in activated_campaigns:
        if ((campaign['queue_name'] == queue_name) and
            (campaign['activated'] == 'True')):
            result = True
    assert result, 'Got wrong campaign ("' + \
        str(activated_campaigns) + \
        '") when asking for activated campaigns for queue: ' + \
        queue_name
