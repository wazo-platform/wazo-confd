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

from lettuce import step, world
from hamcrest import assert_that, has_entry, equal_to, has_item


@step(u'Then I get an empty list')
def then_i_get_an_empty_list(step):
    user_response = world.response.data
    assert_that(user_response, has_entry('total', 0))
    assert_that(user_response, has_entry('items', []))


@step(u'Then I get a response with status "([^"]*)"')
def then_i_get_a_response_with_status_group1(step, status):
    status_code = int(status)
    error_msg = "response received: %s" % world.response.data
    assert_that(world.response.status, equal_to(status_code), error_msg)


@step(u'Then I get an error message "([^"]*)"')
def then_i_get_an_error_message_group1(step, error_message):
    assert_that(world.response.data, has_item(error_message))
