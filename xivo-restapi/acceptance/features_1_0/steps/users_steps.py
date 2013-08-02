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

from lettuce import step
from lettuce.registry import world
from xivo_dao import user_dao, voicemail_dao, \
    extensions_dao, queue_member_dao, \
    rightcall_dao, rightcall_member_dao, callfilter_dao, dialaction_dao, \
    phonefunckey_dao, schedule_dao, user_line_dao
from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.phonefunckey import PhoneFunckey
from xivo_dao.alchemy.rightcall import RightCall
from xivo_dao.alchemy.schedule import Schedule
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.data_handler.extension import dao as extension_dao
from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.user_line_extension import dao as user_line_extension_dao
from helpers.rest_users import RestUsers

rest_users = RestUsers()


@step('Given there is a user "([^"]*)"$')
def given_there_is_a_user(step, fullname):
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
    world.result = rest_users.get_all_users().data['items']


@step(u'Then I get a list with "([^"]*)" and "([^"]*)"')
def then_i_get_a_list_with_group1_and_group2(step, fullname1, fullname2):
    assert len(world.result) >= 2
    processed_result = [[item['firstname'], item['lastname']] for item in world.result]
    assert fullname1.split(" ") in processed_result
    assert fullname2.split(" ") in processed_result


@step(u'When I ask for the user "([^"]*)" using its id')
def when_i_ask_for_the_user_group1_using_its_id(step, fullname):
    userid = rest_users.id_from_fullname(fullname)
    world.result = rest_users.get_user(userid).data


@step(u'Then I get a single user "([^"]*)"')
def then_i_get_a_single_user_group1(step, fullname):
    (firstname, lastname) = rest_users.decompose_fullname(fullname)
    assert world.result['firstname'] == firstname
    assert world.result['lastname'] == lastname


@step(u'When I create a user "([^"]*)" with description "([^"]*)" and with ctiprofileid "([^"]*)"')
def when_i_create_a_user_group1_with_description_group2(step, fullname, description, ctiprofileid):
    world.result = rest_users.create_user(fullname, description, int(ctiprofileid))


@step(u'Then I get a response with status "([^"]*)"')
def then_i_get_a_response_with_status_group1(step, status):
    assert world.result.status == int(status), world.result.data


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
    userid = rest_users.id_from_fullname(original_fullname)
    world.result = rest_users.update_user(userid, lastname=new_lastname)


@step(u'Then I have a user "([^"]*)"$')
def then_i_have_a_user_group1(step, fullname):
    userid = rest_users.id_from_fullname(fullname)
    assert userid is not None and userid > 0


@step(u'Then the user "([^"]*)" is actually deleted')
def then_the_user_group1_is_actually_deleted(step, fullname):
    userid = rest_users.id_from_fullname(fullname)
    assert userid is None


@step(u'When I create a user "([^"]*)" with an field "([^"]*)" of value "([^"]*)"')
def when_i_create_a_user_group1_with_an_field_group2_of_value_group3(step, fullname, fieldname, fieldvalue):
    world.result = rest_users.create_user_with_field(fullname, fieldname, fieldvalue)


@step(u'Then I get an error message "([^"]*)"')
def then_i_get_an_error_message_group1(step, error_message):
    assert world.result.data[0] == error_message


@step(u'When I update the user "([^"]*)" with a field "([^"]*)" of value "([^"]*)"')
def when_i_update_the_user_group1_with_a_field_group2_of_value_group3(step, fullname, field, value):
    userid = rest_users.id_from_fullname(fullname)
    world.result = rest_users.update_user_with_field(userid, field, value)


@step(u'Given there is a user "([^"]*)" with a voicemail')
def given_there_is_a_user_with_a_voicemail(step, fullname):
    step.given('Given there is a user "%s"' % fullname)
    userid = rest_users.id_from_fullname(fullname)
    user = user_dao.get(userid)
    world.voicemailid = user.voicemailid
    if world.voicemailid is None:
        step.given('Given there is a voicemail with fullname "%s" and with number "123"' % fullname)
        world.voicemailid = voicemail_dao.id_from_mailbox('123', 'default')
        user_dao.update(user.id, {'voicemailid': world.voicemailid})


@step(u'When I update this user with a first name "([^"]*)" and a last name "([^"]*)"')
def when_i_update_the_user_group1_with_a_first_name_group2_and_a_last_name_group3(step, newfirstname, newlastname):
    world.result = rest_users.update_user(world.userid, firstname=newfirstname, lastname=newlastname)


@step(u'Then this user has a voicemail "([^"]*)"')
def then_i_have_a_user_group1_with_a_voicemail_group1(step, voicemail_fullname):
    voicemail = rest_users.voicemail_from_user(world.userid)
    assert voicemail.fullname == voicemail_fullname


@step(u'When I ask for a user with a non existing id')
def when_i_ask_for_a_user_with_a_non_existing_id(step):
    world.result = rest_users.get_user(rest_users.generate_unexisting_id())


@step(u'When I update a user with a non existing id with the last name "([^"]*)"')
def when_i_update_a_user_with_a_non_existing_id_with_the_last_name_group1(step, lastname):
    generated_id = rest_users.generate_unexisting_id()
    world.result = rest_users.update_user(generated_id, lastname)


@step(u'Given there is a user "([^"]*)" with a line "([^"]*)"$')
def given_there_is_a_user_group1_with_a_line_group2(step, fullname, linenumber):
    world.userid, world.lineid, world.user_line_extension_id = rest_users.create_user_with_sip_line(fullname, linenumber)


@step(u'Then I have a user "([^"]*)" with a line "([^"]*)"')
def then_i_have_a_user_group1_with_a_line_group2(step, fullname, linenumber):
    (firstname, lastname) = rest_users.decompose_fullname(fullname)
    matching = None
    for item in world.result:
        if(item['firstname'] == firstname and item['lastname'] == lastname):
            matching = item
            break
    assert matching is not None
    assert 'line' in matching
    assert matching['line']['number'] == linenumber


@step(u'Then I delete this line')
def then_i_delete_this_line(step):
    user_line_extension = user_line_extension_dao.get(world.user_line_extension_id)
    extension = extension_dao.get(user_line_extension.extension_id)
    line = line_dao.get(world.lineid)

    user_line_extension_dao.delete(user_line_extension)
    extension_dao.delete(extension)
    line_dao.delete(line)


@step(u'Then I have a single user "([^"]*)" with a line "([^"]*)"')
def then_i_have_a_single_user_group1_with_a_line_group2(step, fullname, linenumber):
    (firstname, lastname) = rest_users.decompose_fullname(fullname)
    assert world.result['firstname'] == firstname
    assert world.result['lastname'] == lastname
    assert 'line' in world.result
    assert world.result['line']['number'] == linenumber


@step(u'Given there is a user "([^"]*)" with a SIP line "([^"]*)"')
def given_there_is_a_user_with_a_sip_line(step, fullname, number):
    world.userid, world.lineid, world.usersipid = rest_users.create_user_with_sip_line(fullname, number)
    world.number = number


@step(u'When I delete this user$')
def when_i_delete_the_user(step):
    world.result = rest_users.delete_user(world.userid)


@step(u'Then this user no longer exists')
def then_this_user_no_longer_exists(step):
    _check_user_features()
    _check_line_features()
    _check_extensions()
    _check_queuemembers()
    _check_rightcallmembers()
    _check_callfiltermember()
    _check_dialaction()
    _check_phonefunckey()
    _check_schedulepath()
    _check_contextmember()
    _check_voicemail()


def _check_user_features():
    try:
        user_dao.get(world.userid)
        assert False
    except LookupError:
        assert True


def _check_line_features():
    assert user_line_dao.find_line_id_by_user_id(world.userid) == []


def _check_extensions():
    assert extensions_dao.get_by_exten(world.number) is None


def _check_queuemembers():
    if hasattr(world, 'interface'):
        result = queue_member_dao.get_queue_members_for_queues()
        processed_result = [item.member_name for item in result if item.member_name == world.interface]
        assert processed_result == [], str(processed_result)


def _check_rightcallmembers():
    result = rightcall_member_dao.get_by_userid(world.userid)
    assert result == []


def _check_callfiltermember():
    result = callfilter_dao.get_callfiltermembers_by_userid(world.userid)
    assert result == []


def _check_dialaction():
    result = dialaction_dao.get_by_userid(world.userid)
    assert result == []


def _check_phonefunckey():
    result = phonefunckey_dao.get_by_userid(world.userid)
    assert result == []


def _check_schedulepath():
    result = schedule_dao.get_schedules_for_user(world.userid)
    assert result == []


def _check_contextmember():
    result = voicemail_dao.get_contextmember(world.voicemailid)
    assert result is None, result


def _check_voicemail():
    assert voicemail_dao.get(world.voicemailid) is None


@step(u'When I delete a non existing user')
def when_i_delete_a_non_existing_user(step):
    world.result = rest_users.delete_user(rest_users.generate_unexisting_id())


@step(u'Given there is a user "([^"]*)" member of the queue "([^"]*)"')
def given_there_is_a_user_member_of_the_queue(step, user, queue):
    world.userid, _, _ = rest_users.create_user_with_sip_line(user, '1000')
    world.interface = user_line_dao.get_line_identity_by_user_id(world.userid)
    queue_member_dao.add_user_to_queue(world.userid, queue)


@step(u'Given there is a rightcall "([^"]*)"')
def given_there_is_a_rightcall(step, rightcallname):
    right = rightcall_dao.get_by_name(rightcallname)
    if right is None:
        right = RightCall(name=rightcallname, passwd='', authorization=0, commented=0, description='')
        rightcall_dao.add(right)


@step(u'Given there is a user "([^"]*)" with the right call "([^"]*)"')
def given_there_is_a_user_with_the_right_call(step, username, rightcallname):
    rightid = rightcall_dao.get_by_name(rightcallname).id
    step.given('Given there is a user "%s"' % username)
    rightcall_member_dao.add_user_to_rightcall(world.userid, rightid)


@step(u'Given there is a call filter "([^"]*)"')
def given_there_is_a_call_filter(step, filtername):
    callfilters = callfilter_dao.get_by_name(filtername)
    if callfilters == []:
        callfilter = Callfilter()
        callfilter.callfrom = 'internal'
        callfilter.type = 'bosssecretary'
        callfilter.bosssecretary = 'bossfirst-serial'
        callfilter.name = filtername
        callfilter.description = ''
        callfilter_dao.add(callfilter)


@step(u'Given there is a user "([^"]*)" with the call filter "([^"]*)"')
def given_there_is_a_user_with_the_call_filter(step, name, callfilter):
    step.given('Given there is a user "%s"' % name)
    world.filterid = callfilter_dao.get_by_name(callfilter)[0].id
    callfilter_dao.add_user_to_filter(world.userid, world.filterid, 'boss')


@step(u'Given there is a user "([^"]*)" with a dialaction')
def given_there_is_a_user_with_a_dialaction(step, fullname):
    step.given('Given there is a user "%s"' % fullname)
    dialaction = Dialaction()
    dialaction.action = 'none'
    dialaction.event = 'answer'
    dialaction.category = 'user'
    dialaction.categoryval = str(world.userid)
    dialaction_dao.add(dialaction)


@step(u'Given there is a user "([^"]*)" with a function key')
def given_there_is_a_user_with_a_function_key(step, fullname):
    step.given('Given there is a user "%s"' % fullname)
    key = PhoneFunckey()
    key.iduserfeatures = world.userid
    key.fknum = 1
    key.label = 'my label'
    phonefunckey_dao.add(key)


@step(u'Given there is a schedule "([^"]*)"')
def given_there_is_a_schedule(step, name):
    schedule = Schedule()
    schedule.name = name
    schedule_dao.add(schedule)
    world.scheduleid = schedule.id


@step(u'Given there is a user "([^"]*)" with this schedule')
def given_there_is_a_user_with_a_schedule(step, fullname):
    step.given('Given there is a user "%s"' % fullname)
    schedule_dao.add_user_to_schedule(world.userid, world.scheduleid)


@step(u'When I delete this user and force voicemail deletion')
def when_i_delete_this_user_and_force_voicemail_deletion(step):
    world.result = rest_users.delete_user(world.userid, True)
