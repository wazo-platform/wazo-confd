# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    equal_to,
    has_entries,
    has_length,
    instance_of,
)

from . import confd
from ..helpers import (
    associations as a,
    fixtures,
)


def test_get_user_line_id_associated_endpoints_sip():
    with fixtures.user() as user, fixtures.line() as line, fixtures.sip() as sip:
        with a.line_endpoint_sip(line, sip), a.user_line(user, line):
            response = confd.users(user['uuid']).lines(line['id']).associated.endpoints.sip.get()
            assert_that(
                response.item,
                has_entries(
                    username=has_length(8),
                    secret=has_length(8),
                    type='friend',
                    host='dynamic',
                    options=instance_of(list),
                )
            )


def test_get_user_line_id_associated_endpoints_sip_when_endpoint_is_sccp():
    with fixtures.user() as user, fixtures.line() as line, fixtures.sccp() as sccp:
        with a.line_endpoint_sccp(line, sccp), a.user_line(user, line):
            response = confd.users(user['uuid']).lines(line['id']).main.associated.endpoints.sip.get()
            assert_that(response.status, equal_to(404))


def test_get_user_line_id_associated_endpoints_sip_when_line_does_not_exist():
    with fixtures.user() as user:
        response = confd.users(user['uuid']).lines(999999).associated.endpoints.sip.get()
        assert_that(response.status, equal_to(404))



def test_get_user_line_id_associated_endpoints_sip_when_user_line_not_associated():
    with fixtures.user() as user, fixtures.line() as line, fixtures.sip() as sip:
        with a.line_endpoint_sip(line, sip):
            response = confd.users(user['uuid']).lines(line['id']).associated.endpoints.sip.get()
            assert_that(response.status, equal_to(404))


def test_get_user_line_main_associated_endpoints_sip():
    with fixtures.user() as user, fixtures.line() as line, fixtures.sip() as sip:
        with a.line_endpoint_sip(line, sip), a.user_line(user, line):
            response = confd.users(user['uuid']).lines.main.associated.endpoints.sip.get()
            assert_that(
                response.item,
                has_entries(
                    username=has_length(8),
                    secret=has_length(8),
                    type='friend',
                    host='dynamic',
                    options=instance_of(list),
                )
            )


def test_get_user_line_main_associated_endpoints_sip_when_endpoint_is_sccp():
    with fixtures.user() as user, fixtures.line() as line, fixtures.sccp() as sccp:
        with a.line_endpoint_sccp(line, sccp), a.user_line(user, line):
            response = confd.users(user['uuid']).lines.main.associated.endpoints.sip.get()
            assert_that(response.status, equal_to(404))


def test_get_user_line_main_associated_endpoints_sip_when_line_does_not_exist():
    with fixtures.user() as user:
        response = confd.users(user['uuid']).lines.main.associated.endpoints.sip.get()
        assert_that(response.status, equal_to(404))

