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

from acceptance.helpers.config import get_config_value

from hamcrest import *
from helpers import extension_helper, extension_ws
from lettuce import step, world


@step(u'Given I have no extensions')
def given_i_have_no_extensions(step):
    extension_helper.delete_all()


@step(u'Given I only have the following extensions:')
def given_i_have_the_following_extensions(step):
    extension_helper.delete_all()
    extension_helper.create_extensions(step.hashes)


@step(u'When I access the list of extensions')
def when_i_access_the_list_of_extensions(step):
    world.response = extension_ws.all_extensions()


@step(u'When I access the extension with id "([^"]*)"')
def when_i_access_the_extension_with_id_group1(step, extension_id):
    world.response = extension_ws.get_extension(extension_id)


@step(u'When I create an empty extension')
def when_i_create_an_empty_extension(step):
    world.response = extension_ws.create_extension({})


@step(u'When I create an extension with the following properties:')
def when_i_create_an_extension_with_the_following_properties(step):
    properties = _extract_extension_properties(step)
    world.response = extension_ws.create_extension(properties)


@step(u'When I delete extension "([^"]*)"')
def when_i_delete_extension_group1(step, extension_id):
    world.response = extension_ws.delete_extension(extension_id)


@step(u'Then I get a list with only the default extensions')
def then_i_get_a_list_with_only_the_default_extensions(step):
    extensions = _filter_out_default_extensions()
    assert_that(extensions, has_length(0))


@step(u'Then I get a list containing the following extensions:')
def then_i_get_a_list_containing_the_following_extensions(step):
    expected_extensions = step.hashes
    extensions = _filter_out_default_extensions()

    entries = [has_entries(e) for e in expected_extensions]
    assert_that(extensions, has_items(*entries))


@step(u'Then I have an extension with the following properties:')
def then_i_have_an_extension_with_the_following_properties(step):
    properties = _extract_extension_properties(step)
    extension = world.response.data

    assert_that(extension, has_entries(properties))


@step(u'Then I get a response with an id')
def then_i_get_a_response_with_an_id(step):
    assert_that(world.response.data, has_entry('id', instance_of(int)))


@step(u'Then I get a response with a link to an extension resource')
def then_i_get_a_response_with_a_link_to_an_extension_resource(step):
    host = get_config_value('xivo', 'hostname')
    port = get_config_value('restapi', 'port')
    extension_id = world.response.data['id']

    expected_url = "https://%s:%s/1.1/extensions/%s" % (host, port, extension_id)

    assert_that(world.response.data,
                has_entry('links', contains(
                    has_entries({
                        'rel': 'extensions',
                        'href': expected_url
                    }))))


@step(u'Then I get a response header with a location for the new extension')
def then_i_get_a_response_header_with_a_location_for_the_new_extension(step):
    extension_id = world.response.data['id']

    assert_that(world.response.headers, has_key('location'))

    location = world.response.headers['Location']
    expected_location = '/1.1/extensions/%s' % extension_id

    assert_that(location, ends_with(expected_location))


@step(u'Then the extension "([^"]*)" no longer exists')
def then_the_extension_group1_no_longer_exists(step, extension_id):
    response = extension_ws.get_extension(extension_id)
    assert_that(response.status, equal_to(404))


def _filter_out_default_extensions():
    assert_that(world.response.data, has_key('items'))
    extensions = [e for e in world.response.data['items'] if e['context'] != 'xivo-features']
    return extensions


def _extract_extension_properties(step):
    properties = step.hashes[0]

    if 'id' in properties:
        properties['id'] = int(properties['id'])

    return properties
