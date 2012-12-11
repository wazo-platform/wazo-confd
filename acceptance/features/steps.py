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



@step(u'When I create a campaign named "([^"]*)"')
def when_i_create_a_campaign_named_campagne_name(step, campaign_name):
    r_campaign = RestCampaign()
    assert r_campaign.create(campaign_name), "Cannot create a campaign"

@step(u'Then I can consult this campaign')
def then_i_can_consult_this_campaign(step):
    r_campaign = RestCampaign()
    r_campaign.create('test_consult_campaign')
    assert r_campaign.list(), "Cannot consult campaign list"




#
#@step('When I start the campaign')
#def when_i_start_the_campaign(step):
#    assert False, 'This step must be implemented'
#
#
#@step('calls placed in the queue are recorded')
#def check_record(step):
#    recordings = -1
#    assert recordings != 0, \
#        "Got %d records" % recordings
