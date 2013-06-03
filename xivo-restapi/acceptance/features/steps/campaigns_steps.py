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
from xivo_dao import queue_dao, record_campaigns_dao, recordings_dao
import datetime

rest_campaign = RestCampaign()
world.callid = '1'
world.result_list = []


@step(u'Given there is no campaign')
def given_there_is_no_campaign(step):
    rest_campaign.delete_all_campaigns()


@step(u'When I create a campaign "([^"]*)"')
def when_i_create_a_campaign_named_campagne_name(step, campaign_name):
    result = rest_campaign.create(campaign_name)
    assert result.data > 0, "Cannot create a campaign"


@step(u'Then I can consult the campaign named "([^"]*)"')
def then_i_can_consult_the_campaign_named_group1(step, campaign_name):
    liste = [item['campaign_name'] for item in rest_campaign.list().data['items']]
    assert campaign_name in liste, "%s not in %s" % (campaign_name, liste)


@step(u'When I ask for activated campaigns for queue "([^"]*)"')
def when_i_ask_for_activated_campaigns_for_queue_group1(step, queue_name):
    queue_id = queue_dao.id_from_name(queue_name)
    world.activated_campaigns = rest_campaign.get_activated_campaigns(queue_id).data['items']
    assert (world.activated_campaigns is not None), "No activated campaign"


@step(u'Then I get a list of activated campaigns with campaign "([^"]*)"')
def then_i_get_a_list_of_activated_campaigns_with_campaign_group1(step, campaign_name):
    campaign_found = _is_campaign_activated(campaign_name)
    assert campaign_found, 'Did not find campaign %s in %s' % (campaign_name, world.activated_campaigns)


def _is_campaign_activated(campaign_name):
    for campaign in world.activated_campaigns:
        if campaign['campaign_name'] == campaign_name and campaign['activated']:
            return True
    return False


@step(u'Given I create a campaign with the following parameters:')
def given_i_create_a_campaign_with_the_following_parameters(step):
    campaign = dict(step.hashes[0])
    if campaign['queue_name'] == '':
        del campaign['queue_name']
    if 'activated' in campaign:
        campaign['activated'] = bool(campaign['activated'])
    world.result = rest_campaign.create(**campaign)
    world.campaign_id = world.result.data


@step(u'When I edit it with the following parameters:')
def when_i_edit_it_with_the_following_parameters(step):
    campaign = step.hashes[0]
    params = dict(campaign)
    params['queue_id'] = queue_dao.id_from_name(campaign['queue_name'])
    del params['queue_name']
    assert rest_campaign.updateCampaign(world.campaign_id, params), "Cannot update campaign %s" % world.campaign_id


@step(u'Then the campaign is actually modified with the following values:')
def then_the_campaign_is_actually_modified_with_the_following_values(step):
    campaign = rest_campaign.get_campaign(world.campaign_id).data['items'][0]
    expected_campaign = step.hashes[0]
    queue_id = queue_dao.id_from_name(expected_campaign['queue_name'])
    assert campaign['campaign_name'] == expected_campaign['campaign_name']
    assert campaign['queue_id'] == queue_id
    assert campaign['start_date'] == expected_campaign['start_date']
    assert campaign['end_date'] == expected_campaign['end_date']


@step(u'Given there is a queue "([^"]*)" and a queue "([^"]*)"')
def given_there_is_a_queue_group1(step, queue1, queue2):
    rest_campaign.queue_create_if_not_exists(queue1)
    rest_campaign.queue_create_if_not_exists(queue2)


@step(u'Given I create an activated campaign "([^"]*)" pointing to queue "([^"]*)" currently running')
def given_i_create_an_activated_campaign_group1_pointing_to_queue_group2_currently_running(step, campaign_name, queue_id):
    now = datetime.datetime.now()
    d = datetime.timedelta(days=1)
    rest_campaign.create(campaign_name, queue_id, True, (now - d).strftime("%Y-%m-%d"),
                         (now + d).strftime("%Y-%m-%d"))


@step(u'Given I create a non activated campaign "([^"]*)" pointing to queue "([^"]*)" currently running')
def given_i_create_a_non_activated_campaign_group1_pointing_to_queue_group2_currently_running(step, campaign_name, queue_id):
    now = datetime.datetime.now()
    d = datetime.timedelta(days=1)
    rest_campaign.create(campaign_name, queue_id, False, (now - d).strftime("%Y-%m-%d"),
                         (now + d).strftime("%Y-%m-%d"))


@step(u'Given I create an activated campaign "([^"]*)" pointing to queue "([^"]*)" currently not running')
def given_i_create_an_activated_campaign_group1_pointing_to_queue_group2_currently_not_running(step, campaign_name, queue_id):
    now = datetime.datetime.now()
    d = datetime.timedelta(days=1)
    rest_campaign.create(campaign_name, queue_id, True, (now + d).strftime("%Y-%m-%d"),
                         (now + 2 * d).strftime("%Y-%m-%d"))


@step(u'When I ask for running and activated campaigns for queue "([^"]*)"')
def when_i_ask_for_running_and_activated_campaigns_for_queue_group1(step, queue_name):
    queue_id = queue_dao.id_from_name(queue_name)
    world.result = rest_campaign.get_running_activated_campaigns_for_queue(str(queue_id))


@step(u'Then I get campaign "([^"]*)", I do not get "([^"]*)", "([^"]*)"')
def then_i_get_campaign_group1_i_do_not_get_group2_group3_group4(step, campaign1, campaign2, campaign3):
    running_campaigns = world.result.data['items']
    list_names = [item['campaign_name'] for item in running_campaigns]
    assert campaign1 in list_names, '%s was not retrieved.' % campaign1
    assert campaign2 not in list_names, '%s was not retrieved.' % campaign2
    assert campaign3 not in list_names, '%s was not retrieved.' % campaign3


@step(u'Then the campaign "([^"]*)" is created with its start date and end date equal to now')
def then_the_campaign_group1_is_created_with_its_start_date_and_end_date_equal_to_now(step, campaign_name):
    liste = rest_campaign.list().data['items']
    result = False
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    for item in liste:
        if (item["campaign_name"] == campaign_name and
           item["start_date"][:10] == now and item["end_date"][:10] == now):
            result = True
    assert result, 'Campaign not created with the current date: '


@step(u'When I create a campaign with the following parameters:')
def when_i_create_a_campaign_with_the_following_parameters(step):
    values = tuple(step.hashes[0].values())

    generated_step = """
    Given I create a campaign with the following parameters:
    | campaign_name | queue_name | start_date | end_date |
    | %s | %s | %s | %s |
    """ % values

    step.behave_as(generated_step)


@step(u'Then I get an error code "([^\']*)" with message "([^\']*)"')
def then_i_get_an_error_code_group1_with_message_group2(step, error_code, message):
    assert str(world.result.status) == error_code, "Got wrong error code: %s" % world.result.status
    assert world.result.data == [message], "Got wrong message: %s" % world.result.data


@step(u'When I ask for all the campaigns')
def when_i_ask_for_all_the_campaigns(step):
    world.result = rest_campaign.list()


@step(u'Then the displayed total is equal to the actual number of campaigns')
def then_the_displayed_total_is_equal_to_the_actual_number_of_campaigns(step):
    error_msg = 'Got total %s but real number was %s' % (
        world.result.data['total'],
        len(world.result.data['items'])
    )
    assert world.result.data['total'] == len(world.result.data['items']), error_msg


@step(u'Given there are at least "([^"]*)" campaigns')
def given_there_are_at_least_group1_campaigns(step, num_of_campaigns):
    res = rest_campaign.list().data
    if res['total'] < int(num_of_campaigns):
        i = res['total']
        now = datetime.datetime.now()
        while(i <= int(num_of_campaigns)):
            d = datetime.timedelta(days=(i + 1))
            oned = datetime.timedelta(days=1)
            rest_campaign.create('campaign_%d' % i, 'test', True,
                                 (now + d).strftime("%Y-%m-%d"), (now + d + oned).strftime("%Y-%m-%d"))
            i += 1
        res = rest_campaign.list().data
    assert res['total'] >= int(num_of_campaigns), 'Not enough campaigns: %s' % res


@step(u'When I ask for a list of campaigns with page "([^"]*)" and page size "([^"]*)"')
def when_i_ask_for_a_list_of_campaigns_with_page_group1_and_page_size_group2(step, page_number, page_size):
    world.result = rest_campaign.paginated_list(int(page_number), int(page_size))


@step(u'Then I get exactly "([^"]*)" campaigns')
def then_i_get_exactly_group1_campaigns(step, num_of_campaigns):
    error_msg = "Got wrong number of campaigns: %s" % world.result.data
    assert len(world.result.data['items']) == int(num_of_campaigns), error_msg


@step(u'Given I ask for a list of campaigns with page "([^"]*)" and page size "([^"]*)"')
def given_i_ask_for_a_list_of_campaigns_with_page_group1_and_page_size_group2(step, page_number, page_size):
    world.result_list.append(rest_campaign.paginated_list(int(page_number), int(page_size)).data)


@step(u'Then the two results do not overlap')
def then_the_two_results_do_not_overlap(step):
    intersection = [item for item in world.result_list[0]['items'] if item in world.result_list[1]['items']]
    assert intersection == [], 'The results overlap: %s' % intersection


@step(u'When I try to create a campaign "([^"]*)" pointing to queue "([^"]*)" with start date "([^"]*)" and end date "([^"]*)"')
def when_i_try_to_create_a_campaign_group1_pointing_to_queue_group2_with_start_date_group3_and_end_date_group4(step, name, queue, start, end):
    world.result = rest_campaign.create_with_errors(name, queue, True, start, end)


@step(u'When I delete the queue "([^"]*)"')
def when_i_delete_the_queue_group1(step, queue_name):
    queue_dao.delete_by_name(queue_name)


@step(u'Then the queue "([^"]*)" is actually deleted')
def then_the_queue_group1_is_actually_deleted(step, queue_name):
    try:
        rest_campaign.get_queue(queue_name)
    except LookupError:
        return

    assert False, "Exception was not raised"


@step(u'Then I can get the campaign "([^"]*)" with an empty queue_id')
def then_i_can_get_the_campaign_group1_with_an_empty_queue_id(step, campaign_name):
    campaign_id = record_campaigns_dao.id_from_name(campaign_name)
    result = rest_campaign.get_campaign(campaign_id).data['items'][0]
    assert result is not None, "No campaign retrieved"
    assert result['queue_id'] is None, "queue_id not null"


@step(u'Given there is at least one recording for the campaign "([^"]*)"')
def given_there_s_at_least_one_recording_for_the_campaign_group1(step, campaign_name):
    campaign_id = record_campaigns_dao.id_from_name(campaign_name)
    agent_no = '4000'
    rest_campaign.add_agent_if_not_exists(agent_no)
    world.callid += '1'

    time_format = "%a, %d %b %Y %H:%M:%S"
    time = datetime.datetime.now().strftime(time_format)

    rest_campaign.add_recording_details(campaign_id, world.callid, '2002', agent_no, time)


@step(u'When I ask to delete the campaign "([^"]*)"')
def when_i_ask_to_delete_the_campaign_group1(step, campaign_name):
    campaign_id = record_campaigns_dao.id_from_name(campaign_name)
    world.result = rest_campaign.delete_campaign(campaign_id)


@step(u'Given there is not any recording for the campaign "([^"]*)"')
def given_there_isn_t_any_recording_for_the_campaign_group1(step, campaign_name):
    recordings_dao.delete_by_campaign_name(campaign_name)


@step(u'Then I get a response with code "([^\']*)" and the campaign is deleted')
def then_i_get_a_response_with_code_group1_and_the_campaign_is_deleted(step, code):
    assert str(world.result.status) == code
    assert record_campaigns_dao.get(world.campaign_id) is None
