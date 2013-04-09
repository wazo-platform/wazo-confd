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

from acceptance.features.steps.helpers.rest_users import RestUsers
from acceptance.features.steps.voicemails_steps import \
    given_there_is_a_voicemail_with_fullname_group1_and_with_number_group2
from lettuce import step
from lettuce.registry import world
from xivo_dao import user_dao, voicemail_dao, line_dao, usersip_dao, \
    extensions_dao, extenumber_dao, contextnummember_dao
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.userfeatures import UserFeatures

result = None
rest_users = RestUsers()


@step('Given there is a user "([^"]*)"$')
def given_there_is_a_user_group1(step, fullname):
    world.userid = rest_users.id_from_fullname(fullname)
    if(world.userid is None):
        (firstname, lastname) = rest_users.decompose_fullname(fullname)
        user = UserFeatures()
        user.firstname = firstname
        user.lastname = lastname
        user.description = 'description'
        user_dao.add_user(user)
        world.userid = user.id


@step(u'When I ask for all the users')
def when_i_ask_for_all_the_users(step):
    global result
    result = rest_users.get_all_users().data['items']


@step(u'Then I get a list with "([^"]*)" and "([^"]*)"')
def then_i_get_a_list_with_group1_and_group2(step, fullname1, fullname2):
    global result
    assert len(result) >= 2
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


@step(u'When I create a user "([^"]*)" with description "([^"]*)" and with ctiprofileid "([^"]*)"')
def when_i_create_a_user_group1_with_description_group2(step, fullname, description, ctiprofileid):
    global result
    result = rest_users.create_user(fullname, description, int(ctiprofileid))


@step(u'Then I get a response with status "([^"]*)"')
def then_i_get_a_response_with_status_group1(step, status):
    global result
    assert result.status == int(status), result.data


@step(u'Then the user "([^"]*)" is actually created with ctiprofileid "([^"]*)" and description "([^"]*)')
def then_the_user_group1_is_actually_created(step, fullname, ctiprofileid, description):
    userid = rest_users.id_from_fullname(fullname)
    request_result = rest_users.get_user(userid).data
    (firstname, lastname) = rest_users.decompose_fullname(fullname)
    assert request_result['firstname'] == firstname
    assert request_result['lastname'] == lastname
    assert request_result['ctiprofileid'] == int(ctiprofileid), "received: " + str(request_result['ctiprofileid']) + " expected: " + ctiprofileid
    assert request_result['description'] == description


@step(u'When I update the user "([^"]*)" with a last name "([^"]*)"')
def when_i_update_the_user_group1_with_a_last_name_group2(step, original_fullname, new_lastname):
    global result
    userid = rest_users.id_from_fullname(original_fullname)
    result = rest_users.update_user(userid, lastname=new_lastname)


@step(u'Then I have a user "([^"]*)"$')
def then_i_have_a_user_group1(step, fullname):
    userid = rest_users.id_from_fullname(fullname)
    assert userid != None and userid > 0


@step(u'Then the user "([^"]*)" is actually deleted')
def then_the_user_group1_is_actually_deleted(step, fullname):
    userid = rest_users.id_from_fullname(fullname)
    assert userid is None


@step(u'When I create a user "([^"]*)" with an field "([^"]*)" of value "([^"]*)"')
def when_i_create_a_user_group1_with_an_field_group2_of_value_group3(step, fullname, fieldname, fieldvalue):
    global result
    result = rest_users.create_user_with_field(fullname, fieldname, fieldvalue)


@step(u'Then I get an error message "([^"]*)"')
def then_i_get_an_error_message_group1(step, error_message):
    global result
    assert result.data[0] == error_message


@step(u'When I update the user "([^"]*)" with a field "([^"]*)" of value "([^"]*)"')
def when_i_update_the_user_group1_with_a_field_group2_of_value_group3(step, fullname, field, value):
    global result
    userid = rest_users.id_from_fullname(fullname)
    result = rest_users.update_user_with_field(userid, field, value)


@step(u'Given there is a user "([^"]*)" with a voicemail')
def given_there_is_a_user_group1_with_a_voicemail(step, fullname):
    given_there_is_a_user_group1(step, fullname)
    userid = rest_users.id_from_fullname(fullname)
    user = user_dao.get(userid)
    if(user.voicemailid is None):
        given_there_is_a_voicemail_with_fullname_group1_and_with_number_group2(step, fullname, '123')
        voicemailid = voicemail_dao.id_from_mailbox('123', 'default')
        user_dao.update(user.id, {'voicemailid': voicemailid})


@step(u'When I update this user with a first name "([^"]*)" and a last name "([^"]*)"')
def when_i_update_the_user_group1_with_a_first_name_group2_and_a_last_name_group3(step, newfirstname, newlastname):
    global result
    result = rest_users.update_user(world.userid, firstname=newfirstname, lastname=newlastname)


@step(u'Then this user has a voicemail "([^"]*)"')
def then_i_have_a_user_group1_with_a_voicemail_group1(step, voicemail_fullname):
    voicemail = rest_users.voicemail_from_user(world.userid)
    print voicemail.fullname, "\n"
    print voicemail_fullname, "\n"
    assert voicemail.fullname == voicemail_fullname


@step(u'When I ask for a user with a non existing id')
def when_i_ask_for_a_user_with_a_non_existing_id(step):
    global result
    result = rest_users.get_user(rest_users.generate_unexisting_id())


@step(u'When I update a user with a non existing id with the last name "([^"]*)"')
def when_i_update_a_user_with_a_non_existing_id_with_the_last_name_group1(step, lastname):
    global result
    generated_id = rest_users.generate_unexisting_id()
    result = rest_users.update_user(generated_id, lastname)


@step(u'Then I delete the user "([^"]*)" from the database')
def then_i_delete_the_user_group1_from_the_database(step, fullname):
    userid = rest_users.id_from_fullname(fullname)
    rest_users.delete_user_from_db(userid)


@step(u'Given there is a user "([^"]*)" with a line "([^"]*)"')
def given_there_is_a_user_group1_with_a_line_group2(step, fullname, linenumber):
    given_there_is_a_user_group1(step, fullname)
    result = line_dao.find_line_id_by_user_id(world.userid)
    if(result == []):
        line = LineFeatures()
        line.iduserfeatures = world.userid
        line.number = linenumber
        line.protocolid = 0
        line.protocol = "sip"
        line.name = "name"
        line.context = "default"
        line.provisioningid = 0
        line_dao.create(line)
        world.lineid = line.id
    else:
        world.lineid = result[0]


@step(u'Then I have a user "([^"]*)" with a line "([^"]*)"')
def then_i_have_a_user_group1_with_a_line_group2(step, fullname, linenumber):
    global result
    (firstname, lastname) = rest_users.decompose_fullname(fullname)
    matching = None
    for item in result:
        if(item['firstname'] == firstname and item['lastname'] == lastname):
            matching = item
            break
    assert matching is not None
    assert 'line' in matching
    assert matching['line']['number'] == linenumber


@step(u'Then I delete this line')
def then_i_delete_this_line(step):
    line_dao.delete(world.lineid)


@step(u'Then I have a single user "([^"]*)" with a line "([^"]*)"')
def then_i_have_a_single_user_group1_with_a_line_group2(step, fullname, linenumber):
    global result
    (firstname, lastname) = rest_users.decompose_fullname(fullname)
    assert result['firstname'] == firstname
    assert result['lastname'] == lastname
    assert 'line' in result
    assert result['line']['number'] == linenumber


@step(u'Given there is a user "([^"]*)" with a SIP line "([^"]*)"')
def given_there_is_a_user_with_a_sip_line(step, fullname, number):
    world.userid, world.lineid, world.usersipid = rest_users.create_user_with_sip_line(fullname, number)
    world.number = number


@step(u'When I delete this user')
def when_i_delete_the_user(step):
    global result
    result = rest_users.delete_user(world.userid)


@step(u'Then no data is remaining in the tables "([^"]*)"')
def then_no_data_is_remaining_in_the_tables(step, tables):
    tables = tables.split(",")
    table_functions = {"userfeatures": _check_user_features,
                       "linefeatures": _check_line_features,
                       "usersip": _check_usersip,
                       "extensions": _check_extensions,
                       "extenumbers": _check_extenumbers,
                       "contextnummembers": _check_contextnummembers}
    for table in tables:
        table_functions[table]()

def _check_user_features():
    try:
        user_dao.get(world.userid)
        assert False
    except LookupError:
        assert True

def _check_line_features():
    assert line_dao.find_line_id_by_user_id(world.userid) == []

def _check_usersip():
    assert usersip_dao.get(world.usersipid) is None

def _check_extensions():
    assert extensions_dao.get_by_exten(world.number) is None

def _check_extenumbers():
    assert extenumber_dao.get_by_exten(world.number) is None

def _check_contextnummembers():
    assert contextnummember_dao.get_by_userid(world.userid) is None
