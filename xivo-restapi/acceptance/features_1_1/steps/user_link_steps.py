# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from hamcrest import *
from lettuce import step, world
from acceptance.features_1_1.steps.helpers import device_helper, provd_helper, user_link_ws
from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.device import dao as device_dao


@step(u'Given I have no link with the following parameters:')
def given_i_have_no_link_with_the_following_parameters(step):
    for link_info in step.hashes:
        userlink = _extract_parameters(link_info)
        world.response = user_link_ws.delete(userlink['id'])


@step(u'When I create an empty link')
def when_i_create_an_empty_link(step):
    world.response = user_link_ws.create_user_link({})


@step(u'When I create the following links:')
def when_i_create_the_following_links(step):
    for link_info in step.hashes:
        userlink = _extract_parameters(link_info)
        world.response = user_link_ws.create_user_link(userlink)


@step(u'When I delete the following links:')
def when_i_delete_the_following_links(step):
    for link_info in step.hashes:
        userlink = _extract_parameters(link_info)
        world.response = user_link_ws.delete(userlink['id'])


@step(u'When I create a link with the following invalid parameters:')
def when_i_create_a_link_with_the_following_invalid_parameters(step):
    parameters = step.hashes[0]
    world.response = user_link_ws.create_user_link(parameters)


@step(u'Then I get the user_links with the following parameters:')
def then_i_get_the_lines_with_the_following_parameters(step):
    for expected_data in step.hashes:
        assert_that(world.response.data['items'], has_item(
            has_entries(_extract_parameters(expected_data))
        ))


@step(u'When I provision my device with my line_id "([^"]*)" and ip "([^"]*)"')
def when_i_provision_my_device_with_my_line_id_group1(step, line_id, device_ip):
    line = line_dao.get(line_id)
    device_helper.provision_device_using_webi(line.provisioning_extension, device_ip)


@step(u'Then the device "([^"]*)" has been provisioned with a configuration:')
def then_the_device_has_been_provisioned_with_a_configuration(step, device_id):
    device = device_dao.get(device_id)
    provd_helper.device_config_has_properties(device, step.hashes)


def _extract_parameters(user_line):
    if 'id' in user_line:
        user_line['id'] = int(user_line['id'])

    if 'extension_id' in user_line:
        user_line['extension_id'] = int(user_line['extension_id'])

    if 'user_id' in user_line:
        user_line['user_id'] = int(user_line['user_id'])

    if 'line_id' in user_line:
        user_line['line_id'] = int(user_line['line_id'])

    if 'main_line' in user_line:
        user_line['main_line'] = user_line['main_line'] == 'True'

    if 'main_user' in user_line:
        user_line['main_user'] = user_line['main_user'] == 'True'

    return user_line
