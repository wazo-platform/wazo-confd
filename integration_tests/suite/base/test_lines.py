# -*- coding: UTF-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals


import re

from ..helpers import config
from . import confd
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers import errors as e
from ..helpers import associations as a

from hamcrest import (assert_that,
                      contains,
                      contains_inanyorder,
                      empty,
                      has_entries,
                      has_entry,
                      has_items,
                      has_length,
                      none,
                      not_)


def test_get_errors():
    fake_line_get = confd.lines(999999).get
    yield s.check_resource_not_found, fake_line_get, 'Line'


def test_post_errors():
    url = confd.lines.post
    for check in error_checks(url):
        yield check


@fixtures.line()
def test_put_errors(line):
    url = confd.lines(line['id']).put
    for check in error_checks(url):
        yield check

    yield s.check_bogus_field_returns_error, url, 'provisioning_code', None
    yield s.check_bogus_field_returns_error, url, 'position', None
    yield s.check_bogus_field_returns_error, url, 'registrar', None
    yield s.check_bogus_field_returns_error, url, 'registrar', 'invalidregistrar'


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'context', 123
    yield s.check_bogus_field_returns_error, url, 'context', 'undefined'
    yield s.check_bogus_field_returns_error, url, 'context', ''
    yield s.check_bogus_field_returns_error, url, 'context', {}
    yield s.check_bogus_field_returns_error, url, 'context', []
    yield s.check_bogus_field_returns_error, url, 'context', None
    yield s.check_bogus_field_returns_error, url, 'provisioning_code', 123456
    yield s.check_bogus_field_returns_error, url, 'provisioning_code', 'number'
    yield s.check_bogus_field_returns_error, url, 'provisioning_code', '123'
    yield s.check_bogus_field_returns_error, url, 'provisioning_code', '1234567'
    yield s.check_bogus_field_returns_error, url, 'provisioning_code', ''
    yield s.check_bogus_field_returns_error, url, 'provisioning_code', {}
    yield s.check_bogus_field_returns_error, url, 'provisioning_code', []
    yield s.check_bogus_field_returns_error, url, 'position', 'one'
    yield s.check_bogus_field_returns_error, url, 'position', ''
    yield s.check_bogus_field_returns_error, url, 'position', 0
    yield s.check_bogus_field_returns_error, url, 'position', {}
    yield s.check_bogus_field_returns_error, url, 'position', []
    yield s.check_bogus_field_returns_error, url, 'registrar', 123
    yield s.check_bogus_field_returns_error, url, 'registrar', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'registrar', {}
    yield s.check_bogus_field_returns_error, url, 'registrar', []
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', 123456
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', {}
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', []
    yield s.check_bogus_field_returns_error, url, 'caller_id_num', '123ABC'
    yield s.check_bogus_field_returns_error, url, 'caller_id_num', ''
    yield s.check_bogus_field_returns_error, url, 'caller_id_num', {}
    yield s.check_bogus_field_returns_error, url, 'caller_id_num', []


@fixtures.line()
def test_delete_errors(line):
    line_url = confd.lines(line['id'])
    line_url.delete()
    yield s.check_resource_not_found, line_url.get, 'Line'


@fixtures.line(context=config.CONTEXT)
def test_get(line):
    expected = has_entries({'context': config.CONTEXT,
                            'position': 1,
                            'device_slot': 1,
                            'name': none(),
                            'protocol': none(),
                            'device_id': none(),
                            'caller_id_name': none(),
                            'caller_id_num': none(),
                            'registrar': 'default',
                            'provisioning_code': has_length(6),
                            'provisioning_extension': has_length(6),
                            'endpoint_sip': none(),
                            'endpoint_sccp': none(),
                            'endpoint_custom': none(),
                            'extensions': empty(),
                            'users': empty()}
                           )

    response = confd.lines(line['id']).get()
    assert_that(response.item, expected)


@fixtures.line()
@fixtures.line()
def test_search(line1, line2):
    expected = has_items(has_entry('id', line1['id']),
                         has_entry('id', line2['id']))

    response = confd.lines.get()
    assert_that(response.items, expected)

    expected = contains(has_entry('id', line1['id']))

    response = confd.lines.get(search=line1['provisioning_code'])
    assert_that(response.items, expected)


def test_create_line_with_fake_context():
    response = confd.lines.post(context='fakecontext')
    response.assert_match(400, e.not_found('Context'))


def test_create_line_with_minimal_parameters():
    expected = has_entries({'context': config.CONTEXT,
                            'position': 1,
                            'device_slot': 1,
                            'name': none(),
                            'protocol': none(),
                            'device_id': none(),
                            'caller_id_name': none(),
                            'caller_id_num': none(),
                            'registrar': 'default',
                            'provisioning_code': has_length(6),
                            'provisioning_extension': has_length(6)}
                           )

    response = confd.lines.post(context=config.CONTEXT)

    response.assert_created('lines')
    assert_that(response.item, expected)


@fixtures.registrar()
def test_create_line_with_all_parameters(registrar):
    expected = has_entries({'context': config.CONTEXT,
                            'position': 2,
                            'device_slot': 2,
                            'name': none(),
                            'protocol': none(),
                            'device_id': none(),
                            'caller_id_name': none(),
                            'caller_id_num': none(),
                            'registrar': registrar['id'],
                            'provisioning_code': "887865",
                            'provisioning_extension': "887865"}
                           )

    response = confd.lines.post(context=config.CONTEXT,
                                position=2,
                                registrar=registrar['id'],
                                provisioning_code="887865")

    assert_that(response.item, expected)


def test_create_line_with_caller_id_raises_error():
    response = confd.lines.post(context=config.CONTEXT,
                                caller_id_name="Jôhn Smîth",
                                caller_id_num="1000")

    response.assert_status(400)


@fixtures.line(provisioning_code="135246")
def test_create_line_with_provisioning_code_already_taken(line):
    response = confd.lines.post(context=config.CONTEXT,
                                provisioning_code="135246")
    response.assert_match(400, re.compile("provisioning_code"))


@fixtures.line()
def test_update_line_with_fake_context(line):
    response = confd.lines(line['id']).put(context='fakecontext')
    response.assert_match(400, e.not_found('Context'))


@fixtures.line()
@fixtures.context()
@fixtures.registrar()
def test_update_all_parameters_on_line(line, context, registrar):
    url = confd.lines(line['id'])
    expected = has_entries({'context': context['name'],
                            'position': 2,
                            'caller_id_name': none(),
                            'caller_id_num': none(),
                            'registrar': registrar['id'],
                            'provisioning_code': '243546'})

    response = url.put(context=context['name'],
                       position=2,
                       registrar=registrar['id'],
                       provisioning_code='243546')
    response.assert_updated()

    response = url.get()
    assert_that(response.item, expected)


@fixtures.line()
def test_update_caller_id_on_line_without_endpoint_raises_error(line):
    response = confd.lines(line['id']).put(caller_id_name="Jôhn Smîth",
                                           caller_id_num="1000")
    response.assert_status(400)


@fixtures.line(position=2)
def test_when_updating_line_then_values_are_not_overwriten_with_defaults(line):
    url = confd.lines(line['id'])

    response = url.put(provisioning_code="768493")
    response.assert_ok()

    line = url.get().item
    assert_that(line, has_entries(position=2, device_slot=2))


@fixtures.line()
def test_when_line_has_no_endpoint_then_caller_id_can_be_set_to_null(line):
    response = confd.lines(line['id']).put(caller_id_name=None,
                                           caller_id_num=None)
    response.assert_updated()


@fixtures.line()
def test_delete_line(line):
    response = confd.lines(line['id']).delete()
    response.assert_deleted()


@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
@fixtures.extension()
@fixtures.device()
def test_delete_line_then_associatons_are_removed(user, line1, line2, extension, device):
    with a.user_line(user, line1, check=False), a.user_line(user, line2, check=False), \
            a.line_extension(line1, extension, check=False), a.line_device(line1, device, check=False):
        response = confd.users(user['id']).lines.get()
        assert_that(response.items, contains_inanyorder(
            has_entries(line_id=line1['id'],
                        main_line=True),
            has_entries(line_id=line2['id'],
                        main_line=False),
        ))
        response = confd.devices(device['id']).lines.get()
        assert_that(response.items, not_(empty()))

        response = confd.extensions(extension['id']).lines.get()
        assert_that(response.items, not_(empty()))

        confd.lines(line1['id']).delete()

        response = confd.users(user['id']).lines.get()
        assert_that(response.items, contains(
            has_entries(line_id=line2['id'],
                        main_line=True)
        ))
        response = confd.devices(device['id']).lines.get()
        assert_that(response.items, empty())

        response = confd.extensions(extension['id']).lines.get()
        assert_that(response.items, empty())
