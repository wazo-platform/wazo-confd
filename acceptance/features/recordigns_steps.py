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
from time import strftime, localtime

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

@step(u'Given there is a campaign named "([^"]*)"')
def given_there_is_a_campaign_named_campaing_name(step, local_campaign_name):
    global campaign_name
    campaign_name = local_campaign_name
    if rest_campaign.list():
        return True
    assert rest_campaign.create(campaign_name + str(random.randint(100, 999))), "Cannot create a campaign"


@step(u'When I save call details for a call referenced by its "([^"]*)" in campaign "([^"]*)"')
def when_i_save_call_details_for_a_call_referenced_by_its_group1_in_campaign_group2(step, local_callid, campaign_name):
    global callid
    callid = local_callid + str(random.randint(1000, 9999))
    assert callid, "Callid null!"
    assert rest_campaign.addRecordingDetails(campaign_name, callid, caller, callee, time, queue_name), "Cannot add call details"


@step(u'Then I can consult these details')
def then_i_can_consult_these_details(step):
    assert rest_campaign.verifyRecordingsDetails(campaign_name), "Recording not found"
