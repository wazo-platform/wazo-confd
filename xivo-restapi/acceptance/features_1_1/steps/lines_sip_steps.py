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

from helpers import line_sip_ws, context_helper, line_sip_helper
from lettuce import step, world


@step(u'Given I only have the following lines:')
def given_i_created_the_following_lines(step):
    line_sip_helper.delete_all()
    for lineinfo in step.hashes:
        line_sip_helper.create_line_sip(lineinfo)


@step(u'When I create an empty SIP line')
def when_i_create_an_empty_line(step):
    world.response = line_sip_ws.create_line_sip({})


@step(u'When I create a line with the following properties:')
def when_i_create_a_line_with_the_following_properties(step):
    properties = _extract_line_properties(step)
    world.response = line_sip_ws.create_line_sip(properties)


@step(u'Given I have an internal context named "([^"]*)"')
def given_i_have_an_internal_context_named_group1(step, context):
    context_helper.create_context(context)


def _extract_line_properties(step):
    return step.hashes[0]
