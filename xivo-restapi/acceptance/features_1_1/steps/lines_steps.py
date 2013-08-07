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

from helpers import line_helper, line_ws
from lettuce import step, world


@step(u'Given I have no lines')
def given_there_are_no_lines(step):
    line_helper.delete_all()


@step(u'When I ask for the list of lines$')
def when_i_ask_for_the_list_of_lines(step):
    world.response = line_ws.all_lines()
