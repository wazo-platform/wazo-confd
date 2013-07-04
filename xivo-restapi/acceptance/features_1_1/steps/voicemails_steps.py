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
from xivo_dao import voicemail_dao
from helpers.rest_voicemail import RestVoicemail

rest_voicemail = RestVoicemail()


@step(u'Given there is a voicemail with fullname "([^"]*)" and with number "([^"]*)"')
def given_there_is_a_voicemail_with_fullname_group1_and_with_number_group2(step, fullname, number):
    voicemailid = voicemail_dao.id_from_mailbox(number, "default")
    if(voicemailid is None):
        world.voicemailid = rest_voicemail.create_voicemail(fullname, number)
    else:
        voicemail = voicemail_dao.get(voicemailid)
        if(voicemail.fullname != fullname):
            voicemail_dao.update(voicemailid, {'fullname': fullname})


@step(u'When I list the voicemails')
def when_i_list_the_voicemails(step):
    world.result = rest_voicemail.list()


@step(u'Then I get at least one voicemail with fullname "([^"]*)" and with number "([^"]*)"')
def then_i_get_one_voicemail_with_fullname_group1_and_with_number_group2(step, fullname, number):
    assert len(world.result.data["items"]) >= 1
    data = world.result.data["items"]
    matching_data = [item for item in data if item['fullname'] == fullname and item['mailbox'] == number]
    assert len(matching_data) > 0


@step(u'When I update the voicemail of number "([^"]*)" with number "([^"]*)" and fullname "([^"]*)" and deleteaftersend "([^"]*)"')
def when_i_update_the_voicemail_of_number_group1_with_number_group2_and_fullname_group3(step, oldnumber, newnumber, newfullname, newdeleteaftersend):
    newdeleteaftersend_bool = bool(newdeleteaftersend)
    world.result = rest_voicemail.update_voicemail(oldnumber, newnumber=newnumber, newfullname=newfullname, newdeleteaftersend=newdeleteaftersend_bool)


@step(u'Then there is a voicemail with number "([^"]*)" and fullname "([^"]*)"')
def then_there_is_a_voicemail_with_number_group1_and_fullname_group2(step, number, fullname):
    local_result = rest_voicemail.list()
    voicemails = local_result.data["items"]
    matching_voicemails = [voicemail for voicemail in voicemails\
                                if voicemail["mailbox"] == number and voicemail["fullname"] == fullname]
    assert len(matching_voicemails) > 0


@step(u'When I update the voicemail of number "([^"]*)" with a field "([^"]*)" of value "([^"]*)"')
def when_i_update_the_voicemail_of_number_group1_with_a_field_group2_of_value_group3(step, number, fieldname, fieldvalue):
    world.result = rest_voicemail.update_voicemail_field(number, fieldname, fieldvalue)


@step(u'Then I get an error message from voicemails webservice "([^"]*)"')
def then_i_get_an_error_message_from_voicemails_webservice_group1(step, message):
    assert world.result.data[0] == message


@step(u'When I update a voicemail with a non existing id')
def when_i_update_a_voicemail_with_a_non_existing_id(step):
    generated_id = rest_voicemail.generate_non_existing_id()
    world.result = rest_voicemail.update_voicemail_by_id(generated_id, {'fullname': 'test 2'})


@step(u'Given there is no voicemail with number "([^"]*)"')
def given_there_is_no_voicemail_with_number_group1(step, number):
    voicemailid = voicemail_dao.id_from_mailbox(number, "default")
    if(voicemailid is not None):
        rest_voicemail.delete_voicemail_from_db(voicemailid)
