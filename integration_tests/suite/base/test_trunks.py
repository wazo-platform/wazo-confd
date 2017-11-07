# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from ..test_api import scenarios as s
from ..test_api import fixtures

from hamcrest import (assert_that,
                      empty,
                      has_entries,
                      has_entry,
                      has_item,
                      is_not,
                      none,
                      not_)
from . import confd


def test_get_errors():
    fake_trunk = confd.trunks(999999).get
    yield s.check_resource_not_found, fake_trunk, 'Trunk'


def test_delete_errors():
    fake_trunk = confd.trunks(999999).delete
    yield s.check_resource_not_found, fake_trunk, 'Trunk'


def test_post_errors():
    url = confd.trunks.post
    for check in error_checks(url):
        yield check


@fixtures.trunk()
def test_put_errors(trunk):
    url = confd.trunks(trunk['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'context', 123
    yield s.check_bogus_field_returns_error, url, 'context', []
    yield s.check_bogus_field_returns_error, url, 'context', {}
    yield s.check_bogus_field_returns_error, url, 'context', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'twilio_incoming', 123
    yield s.check_bogus_field_returns_error, url, 'twilio_incoming', []
    yield s.check_bogus_field_returns_error, url, 'twilio_incoming', {}


@fixtures.context(name='search')
@fixtures.context(name='hidden')
@fixtures.trunk(context='search')
@fixtures.trunk(context='hidden')
def test_search(_, __, trunk, hidden):
    url = confd.trunks
    searches = {'context': 'search'}

    for field, term in searches.items():
        yield check_search, url, trunk, hidden, field, term


def check_search(url, trunk, hidden, field, term):
    response = url.get(search=term)

    expected = has_item(has_entry(field, trunk[field]))
    not_expected = has_item(has_entry(field, hidden[field]))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))

    response = url.get(**{field: trunk[field]})

    expected = has_item(has_entry('id', trunk['id']))
    not_expected = has_item(has_entry('id', hidden['id']))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))


@fixtures.context(name='sort1')
@fixtures.context(name='sort2')
@fixtures.trunk(context='sort1')
@fixtures.trunk(context='sort2')
def test_sorting_offset_limit(_, __, trunk1, trunk2):
    url = confd.trunks.get
    yield s.check_sorting, url, trunk1, trunk2, 'context', 'sort'

    yield s.check_offset, url, trunk1, trunk2, 'context', 'sort'
    yield s.check_offset_legacy, url, trunk1, trunk2, 'context', 'sort'

    yield s.check_limit, url, trunk1, trunk2, 'context', 'sort'


@fixtures.trunk()
def test_get(trunk):
    response = confd.trunks(trunk['id']).get()
    assert_that(response.item, has_entries(id=trunk['id'],
                                           context=trunk['context'],
                                           twilio_incoming=trunk['twilio_incoming'],
                                           endpoint_sip=none(),
                                           endpoint_custom=none(),
                                           outcalls=empty()))


def test_create_minimal_parameters():
    response = confd.trunks.post()
    response.assert_created('trunks')

    assert_that(response.item, has_entries(id=not_(empty())))


@fixtures.context()
def test_create_all_parameters(context):
    response = confd.trunks.post(context=context['name'], twilio_incoming=True)
    response.assert_created('trunks')

    assert_that(response.item, has_entries(context=context['name'], twilio_incoming=True))


@fixtures.trunk()
def test_edit_minimal_parameters(trunk):
    parameters = {}

    response = confd.trunks(trunk['id']).put(**parameters)
    response.assert_updated()


@fixtures.context(name='not_default')
@fixtures.trunk()
def test_edit_all_parameters(context, trunk):
    parameters = {
        'context': context['name'],
        'twilio_incoming': True,
    }

    response = confd.trunks(trunk['id']).put(**parameters)
    response.assert_updated()

    response = confd.trunks(trunk['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.trunk()
def test_delete(trunk):
    response = confd.trunks(trunk['id']).delete()
    response.assert_deleted()
