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
from xivo_dao.data_handler.context.model import ContextType
from xivo_lettuce.manager_ws import context_manager_ws


@step(u'Given I have the following context:')
def given_i_have_the_following_extensions(step):
    for context_data in step.hashes:
        context_manager_ws.add_or_replace_context(context_data['name'],
                                                  context_data['name'],
                                                  ContextType.internal)
        context_manager_ws.update_contextnumbers_user(context_data['name'],
                                                      context_data['numberbeg'],
                                                      context_data['numberend'])
