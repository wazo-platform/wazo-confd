# -*- coding: utf-8 -*-
# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from hamcrest import (
    assert_that,
    contains,
    has_entries,
    has_entry,
    has_items,
    has_length,
    none,
    not_none,
)

from . import confd
from ..helpers import (
    config,
    errors as e,
    fixtures,
    scenarios as s,
)


def test_get_errors():
    fake_line_get = confd.lines_sip(999999).get
    yield s.check_resource_not_found, fake_line_get, 'Line'


def test_post_errors():
    empty_post = confd.lines_sip.post
    line_post = confd.lines_sip(context=config.CONTEXT, device_slot=1).post

    yield s.check_missing_required_field_returns_error, empty_post, 'context'

    yield s.check_bogus_field_returns_error, line_post, 'context', 123
    yield s.check_bogus_field_returns_error, line_post, 'device_slot', 'slot'
    yield s.check_bogus_field_returns_error, line_post, 'callerid', 'invalidcallerid'
    yield s.check_bogus_field_returns_error, line_post, 'secret', [{}]
    yield s.check_bogus_field_returns_error, line_post, 'username', [{}]


@fixtures.line_sip()
def test_put_errors(line):
    line_put = confd.lines_sip(line['id']).put

    yield s.check_missing_required_field_returns_error, line_put, 'context'
    yield s.check_bogus_field_returns_error, line_put, 'context', 123
    yield s.check_bogus_field_returns_error, line_put, 'device_slot', 'invalid'
    yield s.check_bogus_field_returns_error, line_put, 'callerid', 'invalidcallerid'
    yield s.check_bogus_field_returns_error, line_put, 'secret', 123
    yield s.check_bogus_field_returns_error, line_put, 'username', 123


@fixtures.line_sip()
def test_delete_errors(line):
    line_url = confd.lines_sip(line['id'])
    line_url.delete()
    yield s.check_resource_not_found, line_url.get, 'Line'


@fixtures.line_sip(context=config.CONTEXT)
def test_get(line):
    response = confd.lines_sip(line['id']).get()
    assert_that(
        response.item,
        has_entries(
            username=has_length(8),
            secret=has_length(8),
            context=config.CONTEXT,
            device_slot=1,
            provisioning_extension=has_length(6),
            callerid=none(),
        )
    )


@fixtures.line_sip()
@fixtures.line_sip()
def test_list(line1, line2):
    response = confd.lines_sip.get()
    assert_that(
        response.items,
        has_items(
            has_entry('id', line1['id']),
            has_entry('id', line2['id']),
        )
    )

    response = confd.lines_sip.get(search=line1['provisioning_extension'])
    assert_that(response.items, contains(has_entry('id', line1['id'])))


def test_create_line_with_fake_context():
    response = confd.lines_sip.post(context='fakecontext', device_slot=1)
    response.assert_match(400, e.not_found('Context'))


def test_create_line_with_minimal_parameters():
    response = confd.lines_sip.post(context=config.CONTEXT, device_slot=1)

    response.assert_created('lines_sip')
    assert_that(
        response.item,
        has_entries(
            callerid=none(),
            context=config.CONTEXT,
            device_slot=1,
            provisioning_extension=has_length(6),
            secret=not_none(),
            username=not_none(),
        )
    )


def test_create_line_with_all_parameters():
    response = confd.lines_sip.post(
        context=config.CONTEXT,
        device_slot=2,
        callerid=u'"Fodé Sanderson" <1000>',
        provisioning_extension=u"333222",
        secret=u"secret",
        username=u"username",
    )

    assert_that(
        response.item,
        has_entries(
            callerid=u'"Fodé Sanderson" <1000>',
            context=config.CONTEXT,
            device_slot=2,
            provisioning_extension=u"333222",
            secret=u"secret",
            username=u"username"
        )
    )


@fixtures.line_sip(provisioning_extension="123456")
def test_create_line_with_provisioning_code_already_taken(line):
    response = confd.lines_sip.post(context=config.CONTEXT, provisioning_extension="123456")
    response.assert_match(400, re.compile("provisioning_code"))


@fixtures.line_sip()
def test_update_line_with_fake_context(line):
    response = confd.lines_sip(line['id']).put(context='fakecontext')
    response.assert_match(400, e.not_found('Context'))


@fixtures.line_sip(callerid=u'"Fodé Sanderson" <1000>"')
@fixtures.context()
def test_update_all_parameters_on_line(line, context):
    url = confd.lines_sip(line['id'])
    response = url.put(
        context=context['name'],
        device_slot=2,
        callerid=u'"Mamàsta Michel" <2000>',
        provisioning_extension='234567',
        secret='newsecret',
        username='newusername',
    )
    response.assert_updated()

    response = url.get()
    assert_that(
        response.item,
        has_entries(
            context=context['name'],
            device_slot=2,
            callerid=u'"Mamàsta Michel" <2000>',
            provisioning_extension='234567',
            secret='newsecret',
            username='newusername'
        )
    )


@fixtures.line_sip(callerid=u'"Fodé Sanderson" <1000>"')
def test_update_null_parameters(line):
    url = confd.lines_sip(line['id'])

    response = url.put(callerid=None)
    response.assert_updated()

    response = url.get()
    assert_that(response.item['callerid'], none())


@fixtures.line_sip()
def test_delete_line(line):
    response = confd.lines_sip(line['id']).delete()
    response.assert_deleted()
