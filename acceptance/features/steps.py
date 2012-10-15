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
from xivo_recording.tests.test_config import TestConfig
from gevent import httplib
from rest_campaign import RestCampaign


testConfig = TestConfig()

@step(u'When I create a campaign named "([^"]*)"')
def when_i_create_a_campaign_named_campagne_name(step, campaign_name):
    r_campaign = RestCampaign()
    assert r_campaign.create(campaign_name),"Cannot create a campaign"
    

    














#
#@step('I create a campaign called ([^"]+) for the queue (\d+)')
#def create_a_campaign_for_queue(step, campaign_name, queue_number):
#    
#    connection = httplib.HTTPConnection(testConfig.XIVO_RECORD_SERVICE_URL)
#    requestURI = "/campagnes/recording/"
#    body = ""
#    headers = ""
#    connection.request("POST", requestURI, body, headers)
#
#    response = connection.getresponse()
#    rHeader = response.getHeader()
#    #assert rHeader == 
#
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
