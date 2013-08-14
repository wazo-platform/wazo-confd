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
from acceptance.features_1_1.steps.helpers import line_helper, line_ws, line_sip_helper
from lettuce import step, world


@step(u'Given I only have the following lines:')
def given_i_created_the_following_lines(step):
    line_helper.delete_all()
    for lineinfo in step.hashes:
        protocol = lineinfo['protocol'].lower()
        if protocol == 'sip':
            line_sip_helper.create_line_sip(lineinfo)
        else:
            line_helper.create(lineinfo)


@step(u'Given I have no lines')
def given_there_are_no_lines(step):
    line_helper.delete_all()


@step(u'When I ask for the list of lines$')
def when_i_ask_for_the_list_of_lines(step):
    world.response = line_ws.all_lines()


@step(u'Then the line "([^"]*)" no longer exists')
def then_the_line_group1_no_longer_exists(step, line_id):
    response = line_ws.get(line_id)
    assert_that(response.status, equal_to(404))
