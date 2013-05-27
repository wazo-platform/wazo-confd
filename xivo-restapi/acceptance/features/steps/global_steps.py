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
from lettuce.registry import world
from xivo_dao import record_campaigns_dao
from xivo_restapi.restapi_config import RestAPIConfig
import httplib
import os


@step(u'When I send a "([^"]*)" request to "([^"]*)"')
def when_i_send_a_group1_request_to_group2(step, method, url):
    connection = httplib.HTTPConnection(
                            RestAPIConfig.XIVO_RECORD_SERVICE_ADDRESS +
                            ":" +
                            str(RestAPIConfig.XIVO_RECORD_SERVICE_PORT)
                        )
    headers = RestAPIConfig.CTI_REST_DEFAULT_CONTENT_TYPE
    connection.request(method, url, None, headers)
    world.status = connection.getresponse().status


@step(u'Then I get a response with status code "([^"]*)"')
def then_i_get_a_response_with_status_code_group1(step, status_code):
    assert world.status == int(status_code), "Expected status was " + status_code + \
                    ", actual was " + str(world.status)


@step(u'When I read the list of recordings for the campaign "([^"]*)" from the database')
def when_i_read_the_list_of_recordings_for_the_campaign_group1_from_the_database(step, campaign_name):
    r_campaign = RestCampaign()
    campaign_id = record_campaigns_dao.id_from_name(campaign_name)
    result = r_campaign.paginated_recordings_list(campaign_id, 1, 10)
    world.recordings_list = result['items']


@step(u'Then I get one and only one item with caller "([^"]*)", agent "([^"]*)" and I can read the returned file')
def then_i_get_one_and_only_one_item_with_caller_group1_agent_group2_and_i_can_read_the_returned_file(step, caller, agent):
    assert len(world.recordings_list) == 1, "Retrieved " + str(len(world.recordings_list))\
                                                 + " recordings instead of 1"
    item = world.recordings_list[0]
    assert item['agent_no'] == agent, "Got wrong agent: " + item['agent_no'] + " instead of " + agent
    assert item['caller'] == caller, "Got wrong agent: " + item['caller'] + " instead of " + caller
    assert os.path.exists(RestAPIConfig.RECORDING_FILE_ROOT_PATH + "/" + item['filename']), \
           "The file " + item['filename'] + " does not exist."
