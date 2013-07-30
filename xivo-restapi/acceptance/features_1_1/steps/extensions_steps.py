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
from helpers import extension_helper, extension_ws
from lettuce import step, world


@step(u'Given I have no extensions')
def given_i_have_no_extensions(step):
    extension_helper.delete_all()


@step(u'When I access the list of extensions')
def when_i_access_the_list_of_extensions(step):
    world.response = extension_ws.all_extensions()


@step(u'Then I get a list with only the default extensions')
def then_i_get_a_list_with_only_the_default_extensions(step):
    extensions = _filter_out_default_extensions()
    assert_that(extensions, has_length(0))




def _filter_out_default_extensions():
    assert_that(world.response.data, has_key('items'))
    extensions = [e for e in world.response.data['items'] if e['context'] != 'xivo-features']
    return extensions
