# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import string
import random

from hamcrest import (
    assert_that,
    contains,
    has_entries,
)

from . import confd
from ..helpers import (
    associations as a,
    fixtures,
    scenarios as s,
    wrappers,
)

FAKE_ID = 999999999
FAKE_UUID = '99999999-9999-9999-9999-999999999999'


def generate_extension():
    exten = ''.join(random.choice(string.digits) for _ in range(10))
    extension = {'exten': exten, 'context': 'default'}
    return extension


class extension(wrappers.IsolatedAction):

    actions = {'generate': generate_extension}


@fixtures.group()
@extension()
def test_associate_errors(group, extension):
    response = confd.groups(FAKE_ID).members.extensions.put(extensions=[extension])
    response.assert_status(404)

    url = confd.groups(group['id']).members.extensions.put
    error_checks(url)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'extensions', 123)
    s.check_bogus_field_returns_error(url, 'extensions', None)
    s.check_bogus_field_returns_error(url, 'extensions', True)
    s.check_bogus_field_returns_error(url, 'extensions', 'string')
    s.check_bogus_field_returns_error(url, 'extensions', [123])
    s.check_bogus_field_returns_error(url, 'extensions', [None])
    s.check_bogus_field_returns_error(url, 'extensions', ['string'])
    s.check_bogus_field_returns_error(url, 'extensions', [{}])

    regex = r'extensions.*priority'
    s.check_bogus_field_returns_error_matching_regex(url, 'extensions', [{'priority': None}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'extensions', [{'priority': 'string'}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'extensions', [{'priority': -1}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'extensions', [{'priority': []}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'extensions', [{'priority': {}}], regex)

    regex = r'extensions.*exten'
    s.check_bogus_field_returns_error_matching_regex(url, 'extensions', [{'exten': None}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'extensions', [{'exten': 123}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'extensions', [{'exten': []}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'extensions', [{'exten': {}}], regex)

    regex = r'extensions.*context'
    s.check_bogus_field_returns_error_matching_regex(url, 'extensions', [{'context': None}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'extensions', [{'context': 123}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'extensions', [{'context': []}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'extensions', [{'context': {}}], regex)


@fixtures.group()
@extension()
def test_associate(group, extension):
    response = confd.groups(group['id']).members.extensions.put(extensions=[extension])
    response.assert_updated()


@fixtures.group()
@extension()
@extension()
@extension()
def test_associate_multiple_with_priority(group, extension1, extension2, extension3):
    extension1['priority'], extension2['priority'], extension3['priority'] = 4, 1, 2
    response = confd.groups(group['id']).members.extensions.put(extensions=[extension1, extension2, extension3])
    response.assert_updated()

    response = confd.groups(group['id']).get()
    assert_that(response.item, has_entries(
        members=has_entries(extensions=contains(
            has_entries(exten=extension2['exten'], context=extension2['context'], priority=1),
            has_entries(exten=extension3['exten'], context=extension3['context'], priority=2),
            has_entries(exten=extension1['exten'], context=extension1['context'], priority=4),
        ))
    ))


@fixtures.group()
@extension()
def test_associate_same_extension(group, extension):
    response = confd.groups(group['id']).members.extensions.put(extensions=[extension, extension])
    response.assert_status(400)


@fixtures.group()
@extension()
@extension()
def test_get_extensions_associated_to_group(group, extension1, extension2):
    with a.group_member_extension(group, extension2, extension1):
        response = confd.groups(group['id']).get()
        assert_that(response.item, has_entries(
            members=has_entries(extensions=contains(
                has_entries(exten=extension2['exten'], context=extension2['context']),
                has_entries(exten=extension1['exten'], context=extension1['context']),
            ))
        ))


@fixtures.group()
@extension()
@extension()
def test_dissociate(group, extension1, extension2):
    with a.group_member_extension(group, extension1, extension2):
        response = confd.groups(group['id']).members.extensions.put(extensions=[])
        response.assert_updated()


@fixtures.group()
@extension()
@extension()
def test_delete_group_when_group_and_extension_associated(group, extension1, extension2):
    with a.group_member_extension(group, extension1, extension2, check=False):
        confd.groups(group['id']).delete().assert_deleted()

        deleted_group = confd.groups(group['id']).get
        s.check_resource_not_found(deleted_group, 'Group')


@fixtures.group()
@extension()
def test_bus_events(group, extension):
    url = confd.groups(group['id']).members.extensions.put
    body = {'extensions': [extension]}
    s.check_bus_event('config.groups.members.extensions.updated', url, body)
