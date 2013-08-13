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

from helpers import user_link_ws, user_helper, line_sip_helper, extension_helper
from lettuce import step, world

from hamcrest import *


@step(u'When I create an empty link')
def when_i_create_an_empty_link(step):
    world.response = user_link_ws.create_user_link({})


@step(u'When I create a link with the following parameters:')
def when_i_create_a_link_with_the_following_parameters(step):
    for data_dict in step.hashes:
        parameters = _extract_parameters(data_dict)
        world.response = user_link_ws.create_user_link(parameters)


@step(u'When I create a link with the following invalid parameters:')
def when_i_create_a_link_with_the_following_invalid_parameters(step):
    parameters = step.hashes[0]
    world.response = user_link_ws.create_user_link(parameters)


@step(u'Given I only have the following users:')
def given_i_created_the_following_users(step):
    user_helper.delete_all()
    for userinfo in step.hashes:
        user_helper.create_user(userinfo)


@step(u'Given I only have the following lines:')
def given_i_created_the_following_lines(step):
    line_sip_helper.delete_all()
    for lineinfo in step.hashes:
        line_sip_helper.create_line_sip(lineinfo)


@step(u'Given I only have the following extensions:')
def given_i_have_the_following_extensions(step):
    extension_helper.delete_all()
    for exteninfo in step.hashes:
        extension_helper.create_extensions([exteninfo])


@step(u'Then I get the user_links with the following parameters:')
def then_i_get_the_lines_with_the_following_parameters(step):
    for expected_data in step.hashes:
        assert_that(world.response.data['items'], has_item(
            has_entries(_extract_parameters(expected_data))
        ))


def _extract_parameters(data_dict):
    user_line = data_dict

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
