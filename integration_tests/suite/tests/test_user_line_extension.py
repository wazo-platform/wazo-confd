# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from __future__ import unicode_literals

from hamcrest import assert_that, has_items, has_entries

from test_api import confd
from test_api import fixtures
from test_api import mocks
from test_api import associations as a
from test_api import errors as e


@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
def test_associate_user_then_line_then_extension(user, line, extension):
    response = confd.users(user['id']).lines.post(line_id=line['id'])
    response.assert_created('users', 'lines')

    response = confd.lines(line['id']).extensions.post(extension_id=extension['id'])
    response.assert_created('lines', 'extensions')


@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
def test_associate_extension_then_line_then_user(user, line, extension):
    response = confd.lines(line['id']).extensions.post(extension_id=extension['id'])
    response.assert_created('lines', 'extensions')

    response = confd.users(user['id']).lines.post(line_id=line['id'])
    response.assert_created('users', 'lines')


@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
def test_dissociate_user_then_line_then_extension(user, line, extension):
    with a.user_line(user, line, check=False), a.line_extension(line, extension, check=False):

        response = confd.users(user['id']).lines(line['id']).delete()
        response.assert_deleted()

        response = confd.lines(line['id']).extensions(extension['id']).delete()
        response.assert_deleted()


@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
def test_dissociate_extension_then_line_then_user(user, line, extension):
    with a.user_line(user, line, check=False), a.line_extension(line, extension, check=False):

        response = confd.lines(line['id']).extensions(extension['id']).delete()
        response.assert_deleted()

        response = confd.users(user['id']).lines(line['id']).delete()
        response.assert_deleted()


@fixtures.user()
@fixtures.line_sip()
@fixtures.extension(context='default')
@fixtures.extension(context='from-extern')
def test_get_line_extension_associations(user, line, internal, incall):
    expected = has_items(has_entries({'line_id': line['id'],
                                     'extension_id': internal['id']}),
                         has_entries({'line_id': line['id'],
                                      'extension_id': incall['id']})
                         )

    with a.user_line(user, line), a.line_extension(line, internal), a.line_extension(line, incall):
        response = confd.lines(line['id']).extensions.get()
        assert_that(response.items, expected)


@fixtures.user()
@fixtures.line_sip()
@fixtures.extension(context='default')
@fixtures.extension(context='from-extern')
def test_associate_line_and_incall(user, line, internal, incall):
    expected = has_entries({'line_id': line['id'],
                            'extension_id': incall['id']})

    with a.user_line(user, line):
        response = confd.lines(line['id']).extensions.post(extension_id=incall['id'])
        assert_that(response.item, expected)


@fixtures.user()
@fixtures.line_sip()
@fixtures.extension(context='default')
@fixtures.extension(context='from-extern')
def test_dissociate_line_and_incall(user, line, internal, incall):
    with a.user_line(user, line), a.line_extension(line, incall, check=False):
        response = confd.lines(line['id']).extensions(incall['id']).delete()
        response.assert_deleted()


@mocks.provd()
@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
@fixtures.device()
def test_update_device_associated_to_sip_line(provd, user, line, extension, device):
    with a.user_line(user, line), a.line_extension(line, extension), a.line_device(line, device):
        response = confd.lines(line['id']).put(caller_id_name="Jôhn Smîth")
        response.assert_updated()

        provd_config = provd.configs.get(device['id'])
        sip_line = provd_config['raw_config']['sip_lines']['1']
        assert_that(sip_line, has_entries({'display_name': 'Jôhn Smîth'}))


@mocks.provd()
@fixtures.user()
@fixtures.line()
@fixtures.sip()
@fixtures.extension()
@fixtures.device()
def test_update_device_associated_to_sip_endpoint(provd, user, line, sip, extension, device):
    with a.line_endpoint_sip(line, sip), a.user_line(user, line), \
            a.line_extension(line, extension), a.line_device(line, device):

        response = confd.endpoints.sip(sip['id']).put(username="myusername",
                                                      secret="mysecret")
        response.assert_updated()

        provd_config = provd.configs.get(device['id'])
        sip_line = provd_config['raw_config']['sip_lines']['1']
        assert_that(sip_line, has_entries({'username': 'myusername',
                                           'password': 'mysecret'}))


@fixtures.user(firstname="Jôhn", lastname="Smîth")
@fixtures.line()
@fixtures.sip()
@fixtures.extension()
def test_caller_name_on_sip_line(user, line, sip, extension):
    with a.line_endpoint_sip(line, sip), a.user_line(user, line), a.line_extension(line, extension):
        response = confd.lines(line['id']).get()
        assert_that(response.item, has_entries({'caller_id_name': 'Jôhn Smîth',
                                                'caller_id_num': extension['exten']}))


@fixtures.user(caller_id='"Jôhn Smîth" <1000>')
@fixtures.line()
@fixtures.sip()
@fixtures.extension()
def test_caller_id_on_sip_line(user, line, sip, extension):
    with a.line_endpoint_sip(line, sip), a.user_line(user, line), a.line_extension(line, extension):
        response = confd.lines(line['id']).get()
        assert_that(response.item, has_entries({'caller_id_name': 'Jôhn Smîth',
                                                'caller_id_num': '1000'}))


@fixtures.user()
@fixtures.line()
@fixtures.sip()
@fixtures.extension()
@fixtures.device()
def test_dissociate_sip_endpoint_associated_to_device(user, line, sip, extension, device):
    with a.line_endpoint_sip(line, sip), a.user_line(user, line), \
            a.line_extension(line, extension), a.line_device(line, device):

        response = confd.lines(line['id']).endpoints.sip(sip['id']).delete()
        response.assert_status(400, e.resource_associated('Line', 'Device'))


@fixtures.user(firstname="Jôhn", lastname="Smîth")
@fixtures.line()
@fixtures.sccp()
@fixtures.extension()
def test_caller_name_on_sccp_line(user, line, sccp, extension):
    with a.line_endpoint_sccp(line, sccp), a.user_line(user, line), a.line_extension(line, extension):
        response = confd.lines(line['id']).get()
        assert_that(response.item, has_entries({'caller_id_name': 'Jôhn Smîth',
                                                'caller_id_num': extension['exten']}))


@fixtures.user(caller_id='"Jôhn Smîth" <1000>')
@fixtures.line()
@fixtures.sccp()
@fixtures.extension()
def test_caller_id_on_sccp_line(user, line, sccp, extension):
    with a.line_endpoint_sccp(line, sccp), a.user_line(user, line), a.line_extension(line, extension):
        response = confd.lines(line['id']).get()
        assert_that(response.item, has_entries({'caller_id_name': 'Jôhn Smîth',
                                                'caller_id_num': '1000'}))


@fixtures.user()
@fixtures.line()
@fixtures.sccp()
@fixtures.extension()
@fixtures.device()
def test_dissociate_sccp_endpoint_associated_to_device(user, line, sccp, extension, device):
    with a.line_endpoint_sccp(line, sccp), a.user_line(user, line), \
            a.line_extension(line, extension), a.line_device(line, device):
        response = confd.lines(line['id']).endpoints.sccp(sccp['id']).delete()
        response.assert_status(400, e.resource_associated('Line', 'Device'))
