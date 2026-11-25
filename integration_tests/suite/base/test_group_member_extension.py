# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random
import string

from hamcrest import assert_that, contains_exactly, empty, has_entries

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers import wrappers
from ..helpers.config import MAIN_TENANT, SUB_TENANT, SUB_TENANT2
from . import confd

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

    url = confd.groups(group['uuid']).members.extensions.put
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
    s.check_bogus_field_returns_error_matching_regex(
        url, 'extensions', [{'priority': None}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'extensions', [{'priority': 'string'}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'extensions', [{'priority': -1}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'extensions', [{'priority': []}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'extensions', [{'priority': {}}], regex
    )

    regex = r'extensions.*exten'
    s.check_bogus_field_returns_error_matching_regex(
        url, 'extensions', [{'exten': None}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'extensions', [{'exten': 123}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'extensions', [{'exten': []}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'extensions', [{'exten': {}}], regex
    )

    regex = r'extensions.*context'
    s.check_bogus_field_returns_error_matching_regex(
        url, 'extensions', [{'context': None}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'extensions', [{'context': 123}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'extensions', [{'context': []}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'extensions', [{'context': {}}], regex
    )


@fixtures.group()
@extension()
def test_associate(group, extension):
    response = confd.groups(group['uuid']).members.extensions.put(
        extensions=[extension]
    )
    response.assert_updated()

    response = confd.groups(group['id']).members.extensions.put(extensions=[extension])
    response.assert_updated()


@fixtures.group()
@extension()
@extension()
@extension()
def test_associate_multiple_with_priority(group, extension1, extension2, extension3):
    extension1['priority'], extension2['priority'], extension3['priority'] = 4, 1, 2
    response = confd.groups(group['uuid']).members.extensions.put(
        extensions=[extension1, extension2, extension3]
    )
    response.assert_updated()

    response = confd.groups(group['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            members=has_entries(
                extensions=contains_exactly(
                    has_entries(
                        exten=extension2['exten'],
                        context=extension2['context'],
                        priority=1,
                    ),
                    has_entries(
                        exten=extension3['exten'],
                        context=extension3['context'],
                        priority=2,
                    ),
                    has_entries(
                        exten=extension1['exten'],
                        context=extension1['context'],
                        priority=4,
                    ),
                )
            )
        ),
    )


@fixtures.group()
@extension()
def test_associate_same_extension(group, extension):
    response = confd.groups(group['uuid']).members.extensions.put(
        extensions=[extension, extension]
    )
    response.assert_status(400)


@fixtures.group()
@extension()
@extension()
def test_get_extensions_associated_to_group(group, extension1, extension2):
    with a.group_member_extension(group, extension2, extension1):
        response = confd.groups(group['uuid']).get()
        assert_that(
            response.item,
            has_entries(
                members=has_entries(
                    extensions=contains_exactly(
                        has_entries(
                            exten=extension2['exten'], context=extension2['context']
                        ),
                        has_entries(
                            exten=extension1['exten'], context=extension1['context']
                        ),
                    )
                )
            ),
        )


@fixtures.group()
@extension()
@extension()
def test_dissociate(group, extension1, extension2):
    with a.group_member_extension(group, extension1, extension2):
        response = confd.groups(group['uuid']).members.extensions.put(extensions=[])
        response.assert_updated()


@fixtures.group()
@extension()
@extension()
def test_delete_group_when_group_and_extension_associated(
    group, extension1, extension2
):
    with a.group_member_extension(group, extension1, extension2, check=False):
        confd.groups(group['uuid']).delete().assert_deleted()

        deleted_group = confd.groups(group['uuid']).get
        s.check_resource_not_found(deleted_group, 'Group')


@fixtures.group()
@extension()
def test_bus_events(group, extension):
    url = confd.groups(group['uuid']).members.extensions.put
    body = {'extensions': [extension]}
    headers = {'tenant_uuid': MAIN_TENANT}

    s.check_event('group_member_extensions_associated', headers, url, body)


def put_extensions(group, extensions):
    def call(**kwargs):
        url = confd.groups(group['uuid']).members.extensions
        return url.put(extensions=extensions, **kwargs)

    return call


def extension_in(context):
    return {'exten': generate_extension()['exten'], 'context': context['name']}


def extensions_of(group):
    response = confd.groups(group['uuid']).get()
    return [
        (extension['exten'], extension['context'])
        for extension in response.item['members']['extensions']
    ]


@fixtures.group(wazo_tenant=MAIN_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT2)
def test_associate_group_outside_tenant(main_group, sibling_group):
    for group in (main_group, sibling_group):
        call = put_extensions(group, [])
        s.check_outside_tenant_not_found(call, 'Group', SUB_TENANT)


@fixtures.context(wazo_tenant=SUB_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT)
def test_associate_sub_tenant_group_from_main_tenant(sub_context, sub_group):
    extension = extension_in(sub_context)
    call = put_extensions(sub_group, [extension])
    s.check_sub_tenant_found(call, MAIN_TENANT, 204)
    assert_that(
        extensions_of(sub_group),
        contains_exactly((extension['exten'], sub_context['name'])),
    )

    put_extensions(sub_group, [])(wazo_tenant=SUB_TENANT).assert_updated()


@fixtures.context(wazo_tenant=MAIN_TENANT)
@fixtures.context(wazo_tenant=SUB_TENANT)
@fixtures.context(wazo_tenant=SUB_TENANT2)
@fixtures.group(wazo_tenant=SUB_TENANT)
def test_associate_extension_context_outside_tenant(
    main_context, sub_context, sibling_context, sub_group
):
    extension = extension_in(sub_context)
    put_extensions(sub_group, [extension])(wazo_tenant=SUB_TENANT).assert_updated()

    unknown_context = {'name': 'unknown-context'}
    for outside in (main_context, sibling_context, unknown_context):
        call = put_extensions(sub_group, [extension_in(outside)])
        response = call(wazo_tenant=SUB_TENANT)
        response.assert_match(400, e.not_found('Context'))
        assert_that(
            extensions_of(sub_group),
            contains_exactly((extension['exten'], sub_context['name'])),
        )

    put_extensions(sub_group, [])(wazo_tenant=SUB_TENANT).assert_updated()


@fixtures.context(wazo_tenant=MAIN_TENANT)
@fixtures.context(wazo_tenant=SUB_TENANT)
@fixtures.group(wazo_tenant=MAIN_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT)
def test_associate_extensions_of_different_tenants(
    main_context, sub_context, main_group, sub_group
):
    call = put_extensions(main_group, [extension_in(sub_context)])
    response = call(wazo_tenant=MAIN_TENANT)
    response.assert_match(400, e.different_tenant())
    call = put_extensions(sub_group, [extension_in(main_context)])
    response = call(wazo_tenant=MAIN_TENANT)
    response.assert_match(400, e.different_tenant())

    assert_that(extensions_of(main_group), empty())
    assert_that(extensions_of(sub_group), empty())


@fixtures.group(wazo_tenant=SUB_TENANT2)
def test_associate_wazo_tenant_not_visible(sibling_group):
    s.check_wazo_tenant_not_visible_refused(put_extensions(sibling_group, []))
