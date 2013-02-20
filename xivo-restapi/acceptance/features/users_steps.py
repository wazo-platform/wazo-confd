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

from acceptance.features.rest_users import RestUsers
from lettuce import step
from xivo_dao import user_dao
from xivo_dao.alchemy.userfeatures import UserFeatures
#the following import is necessary to laod CtiProfiles' definition:
from xivo_dao.alchemy.cti_profile import CtiProfile

result = None
rest_users = RestUsers()


@step(u'Given there is no user')
def given_there_is_no_user(step):
    user_dao.delete_all()


@step(u'Given there is a user "([^"]*)"')
def given_there_is_a_user_group1(step, fullname):
    (firstname, lastname) = rest_users.decompose_fullname(fullname)
    user = UserFeatures()
    user.firstname = firstname
    user.lastname = lastname
    user.description = 'description'
    user_dao.add_user(user)


@step(u'When I ask for all the users')
def when_i_ask_for_all_the_users(step):
    global result
    result = rest_users.get_all_users().data['items']


@step(u'Then I get a list with "([^"]*)" and "([^"]*)"')
def then_i_get_a_list_with_group1_and_group2(step, fullname1, fullname2):
    global result
    assert len(result) == 2
    processed_result = [[item['firstname'], item['lastname']] for item in result]
    assert fullname1.split(" ") in processed_result
    assert fullname2.split(" ") in processed_result


@step(u'When I ask for the user "([^"]*)" using its id')
def when_i_ask_for_the_user_group1_using_its_id(step, fullname):
    global result
    userid = rest_users.id_from_fullname(fullname)
    result = rest_users.get_user(userid).data


@step(u'Then I get a single user "([^"]*)"')
def then_i_get_a_single_user_group1(step, fullname):
    global result
    (firstname, lastname) = rest_users.decompose_fullname(fullname)
    assert result['firstname'] == firstname
    assert result['lastname'] == lastname


@step(u'When I create a user "([^"]*)" with description "([^"]*)"')
def when_i_create_a_user_group1_with_description_group2(step, fullname, description):
    global result
    result = rest_users.create_user(fullname, description)


@step(u'Then I get a response with status "([^"]*)"')
def then_i_get_a_response_with_status_group1(step, status):
    global result
    assert result.status == int(status)


@step(u'Then the user "([^"]*)" is actually created')
def then_the_user_group1_is_actually_created(step, fullname):
    userid = rest_users.id_from_fullname(fullname)
    request_result = rest_users.get_user(userid)
    (firstname, lastname) = rest_users.decompose_fullname(fullname)
    assert request_result['firstname'] == firstname
    assert request_result['lastname'] == lastname
