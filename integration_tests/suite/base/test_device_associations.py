# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from . import mocks, provd, db, confd
from ..helpers import (
    associations as a,
    config,
    errors as e,
    fixtures,
    helpers as h,
)


def test_when_extension_updated_on_sip_line_then_provd_is_updated():
    with fixtures.user() as user, fixtures.line() as line, fixtures.sip() as sip, fixtures.extension() as extension, fixtures.device() as device:
        exten = h.extension.find_available_exten(config.CONTEXT)
        line_cid = h.extension.find_available_exten(config.CONTEXT, exclude=[exten])

        with a.line_endpoint_sip(line, sip), a.user_line(user, line), \
            a.line_extension(line, extension), a.line_device(line, device):

            response = confd.extensions(extension['id']).put(exten=exten)
            response.assert_updated()

            response = confd.lines(line['id']).put(caller_id_num=line_cid)
            response.assert_updated()

            provd_config = provd.configs.get(device['id'])
            sip_line = provd_config['raw_config']['sip_lines']['1']
            assert_that(sip_line, has_entries(number=exten))



def test_when_caller_id_updated_on_line_then_provd_is_updated():
    with fixtures.user() as user, fixtures.line_sip() as line, fixtures.extension() as extension, fixtures.device() as device:
        with a.user_line(user, line), a.line_extension(line, extension), a.line_device(line, device):
            response = confd.lines(line['id']).put(caller_id_name="jôhn smîth", caller_id_num="1000")
            response.assert_updated()

            provd_config = provd.configs.get(device['id'])
            sip_line = provd_config['raw_config']['sip_lines']['1']
            assert_that(sip_line, has_entries({'display_name': 'jôhn smîth',
                                               'number': extension['exten']}))


def test_when_caller_id_updated_on_user_then_provd_is_updated():
    with fixtures.user() as user, fixtures.line_sip() as line, fixtures.extension() as extension, fixtures.device() as device:
        with a.user_line(user, line), a.line_extension(line, extension), a.line_device(line, device):
            response = confd.users(user['id']).put(caller_id='"rôger rabbit" <1000>')
            response.assert_updated()

            provd_config = provd.configs.get(device['id'])
            sip_line = provd_config['raw_config']['sip_lines']['1']
            assert_that(sip_line, has_entries({'display_name': 'rôger rabbit',
                                               'number': extension['exten']}))


@mocks.provd()
def test_when_sip_username_and_password_are_updated_then_provd_is_updated(provd):
    with fixtures.user() as user, fixtures.line() as line, fixtures.sip() as sip, fixtures.extension() as extension, fixtures.device() as device:
        with a.line_endpoint_sip(line, sip), a.user_line(user, line), \
            a.line_extension(line, extension), a.line_device(line, device):

            response = confd.endpoints.sip(sip['id']).put(username="myusername",
                                                          secret="mysecret")
            response.assert_updated()

            provd_config = provd.configs.get(device['id'])
            sip_line = provd_config['raw_config']['sip_lines']['1']
            assert_that(sip_line, has_entries({'auth_username': 'myusername',
                                               'username': 'myusername',
                                               'password': 'mysecret'}))


def test_updating_line_associated_with_autoprov_device_does_not_fail(line, sip, device):
    with fixtures.line() as line, fixtures.sip() as sip, fixtures.autoprov() as device:
        with a.line_endpoint_sip(line, sip, check=False):
            with db.queries() as queries:
                queries.associate_line_device(line['id'], device['id'])
            response = confd.lines(line['id']).put()
            response.assert_ok()


def test_updating_user_line_or_extension_associated_with_autoprov_device_does_not_fail():
    with fixtures.user() as user, fixtures.line() as line, fixtures.sip() as sip, fixtures.extension() as extension, fixtures.autoprov() as device:
        with a.line_endpoint_sip(line, sip, check=False), a.line_extension(line, extension, check=False), \
            a.user_line(user, line, check=False):

            with db.queries() as queries:
                queries.associate_line_device(line['id'], device['id'])

            response = confd.endpoints.sip(sip['id']).put()
            response.assert_ok()

            response = confd.lines(line['id']).put()
            response.assert_ok()

            response = confd.users(user['id']).put()
            response.assert_ok()

            response = confd.extensions(extension['id']).put()
            response.assert_ok()


def test_given_extension_associated_to_sccp_line_when_updated_then_cid_num_updated():
    with fixtures.user() as user, fixtures.line() as line, fixtures.sccp() as sccp, fixtures.extension() as extension:
        exten = h.extension.find_available_exten(config.CONTEXT)

        with a.line_endpoint_sccp(line, sccp), a.line_extension(line, extension), a.user_line(user, line):
            confd.extensions(extension['id']).put(exten=exten).assert_updated()

            response = confd.lines(line['id']).get()
            assert_that(response.item, has_entries(caller_id_num=exten))



def test_dissociate_line_associated_to_a_device():
    with fixtures.user() as user, fixtures.line_sip() as line, fixtures.extension() as extension, fixtures.device() as device:
        with a.line_extension(line, extension), a.user_line(user, line), a.line_device(line, device):
            response = confd.lines(line['id']).extensions(extension['id']).delete()
            response.assert_match(400, e.resource_associated('Line', 'Device'))


def test_dissociate_user_line_when_device_is_associated():
    with fixtures.user() as user, fixtures.line_sip() as line, fixtures.extension() as extension, fixtures.device() as device:
        with a.user_line(user, line), a.line_extension(line, extension), a.line_device(line, device):
            response = confd.users(user['id']).lines(line['id']).delete()
            response.assert_match(400, e.resource_associated('Line', 'Device'))


def test_dissociate_sip_endpoint_associated_to_device():
    with fixtures.user() as user, fixtures.line() as line, fixtures.sip() as sip, fixtures.extension() as extension, fixtures.device() as device:
        with a.line_endpoint_sip(line, sip), a.user_line(user, line), a.line_extension(line, extension), a.line_device(line, device):
            response = confd.lines(line['id']).endpoints.sip(sip['id']).delete()
            response.assert_match(400, e.resource_associated())


def test_dissociate_sccp_endpoint_associated_to_device():
    with fixtures.user() as user, fixtures.line() as line, fixtures.extension() as extension, fixtures.sccp() as sccp, fixtures.device() as device:
        with a.line_endpoint_sccp(line, sccp), a.user_line(user, line), a.line_extension(line, extension), a.line_device(line, device):
            response = confd.lines(line['id']).endpoints.sccp(sccp['id']).delete()
            response.assert_match(400, e.resource_associated())
