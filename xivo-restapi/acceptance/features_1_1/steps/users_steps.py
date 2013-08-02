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

from acceptance.helpers.config import get_config_value
from hamcrest import assert_that, has_entry, has_entries, has_key, equal_to, \
    has_item, instance_of, ends_with, contains
from helpers import user_helper, user_ws
from lettuce import step, world


@step(u'Given there are no users')
def given_there_are_no_users(step):
    user_helper.delete_all()


@step(u'Given there are only the following users:')
def given_there_are_the_following_users(step):
    user_helper.delete_all()
    for userinfo in step.hashes:
        user_helper.create_user(userinfo)


@step(u'When I ask for the list of users$')
def when_i_ask_for_the_list_of_users(step):
    world.response = user_ws.all_users()


@step(u'When I ask for the user with id "([^"]*)"')
def when_i_ask_for_the_user_with_id_group1(step, userid):
    world.response = user_ws.get_user(userid)


@step(u'When I search for the user "([^"]*)"')
def when_i_search_for_user_group1(step, search):
    world.response = user_ws.user_search(search)


@step(u'When I create an empty user')
def when_i_create_an_empty_user(step):
    world.response = user_ws.create_user({})


@step(u'When I create users with the following parameters:')
def when_i_create_users_with_the_following_parameters(step):
    for userinfo in step.hashes:
        world.response = user_ws.create_user(userinfo)


@step(u'When I update the user with id "([^"]*)" using the following parameters:')
def when_i_update_the_user_with_id_group1_using_the_following_parameters(step, userid):
    userinfo = _get_user_info(step.hashes)
    world.response = user_ws.update_user(userid, userinfo)


@step(u'When I delete the user with id "([^"]*)"')
def when_i_delete_the_user_with_id_group1(step, userid):
    world.response = user_ws.delete_user(userid)


@step(u'Then I get a list with the following users:')
def then_i_get_a_list_with_the_following_users(step):
    user_response = world.response.data
    expected_users = step.hashes

    assert_that(user_response, has_key('items'))
    users = user_response['items']

    for expected_user, user in zip(expected_users, users):
        assert_that(user, has_entries(expected_user))


@step(u'Then I get a response header with a location for the new user')
def then_i_get_a_response_header_with_a_location_for_the_new_user(step):
    userid = world.response.data['id']

    assert_that(world.response.headers, has_key('location'))

    location = world.response.headers['Location']
    expected_location = '/1.1/users/%s' % userid

    assert_that(location, ends_with(expected_location))


@step(u'Then I get a user with the following properties:')
def then_i_get_a_user_with_the_following_properties(step):
    user = world.response.data
    expected_user = _get_user_info(step.hashes)

    assert_that(user, has_entries(expected_user))


def _get_user_info(hashes):
    userinfo = hashes[0]

    if 'id' in userinfo:
        userinfo['id'] = int(userinfo['id'])

    return userinfo


@step(u'Then I get a response with user links')
def then_i_get_a_response_with_user_links(step):
    host = get_config_value('xivo', 'hostname')
    port = get_config_value('restapi', 'port')
    user_id = world.response.data['id']

    expected_url = "https://%s:%s/1.1/users/%s" % (host, port, user_id)

    assert_that(world.response.data,
                has_entry('links', contains(
                    has_entries({
                        'rel': 'users',
                        'href': expected_url
                    }))))


@step(u'Then the created user has the following parameters:')
def then_the_created_user_has_the_following_parameters(step):
    userid = world.response.data['id']

    user = user_ws.get_user(userid).data
    expected_user = _get_user_info(step.hashes)

    assert_that(user, has_entries(expected_user))


@step(u'Then I get a response with a user id')
def then_i_get_a_response_with_a_user_id(step):
    assert_that(world.response.data, has_entry('id', instance_of(int)))


@step(u'Then the user with id "([^"]*)" no longer exists')
def then_the_user_with_id_group1_no_longer_exists(step, userid):
    response = user_ws.get_user(userid)
    assert_that(response.status, equal_to(404))
