# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import concurrent.futures

from hamcrest import (
    all_of,
    assert_that,
    empty,
    has_entries,
    has_entry,
    has_item,
    has_items,
    is_not,
    not_,
)
from wazo_test_helpers.hamcrest.uuid_ import uuid_

from . import confd, BaseIntegrationTest
from ..helpers import errors as e, fixtures, scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT, ALL_TENANTS, DELETED_TENANT


def test_get_errors():
    fake_context = confd.contexts(999999).get
    s.check_resource_not_found(fake_context, 'Context')


def test_delete_errors():
    fake_context = confd.contexts(999999).delete
    s.check_resource_not_found(fake_context, 'Context')


def test_post_errors():
    url = confd.contexts.post
    error_checks(url)

    s.check_bogus_field_returns_error(url, 'label', 123)
    s.check_bogus_field_returns_error(url, 'label', True)
    s.check_bogus_field_returns_error(url, 'label', None)
    s.check_bogus_field_returns_error(url, 'label', '')
    s.check_bogus_field_returns_error(url, 'label', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'label', [])
    s.check_bogus_field_returns_error(url, 'label', {})

    s.check_bogus_field_returns_error(url, 'name', 123, None, 'label')
    s.check_bogus_field_returns_error(url, 'name', True, None, 'label')
    s.check_bogus_field_returns_error(url, 'name', None, None, 'label')
    s.check_bogus_field_returns_error(url, 'name', '', None, 'label')
    s.check_bogus_field_returns_error(url, 'name', s.random_string(129), None, 'label')
    s.check_bogus_field_returns_error(url, 'name', [], None, 'label')
    s.check_bogus_field_returns_error(url, 'name', {}, None, 'label')


@fixtures.context()
def test_put_errors(context):
    url = confd.contexts(context['id']).put
    error_checks(url)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'label', 123)
    s.check_bogus_field_returns_error(url, 'label', True)
    s.check_bogus_field_returns_error(url, 'label', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'label', [])
    s.check_bogus_field_returns_error(url, 'label', {})
    s.check_bogus_field_returns_error(url, 'name', 123, None, 'label')
    s.check_bogus_field_returns_error(url, 'name', True, None, 'label')
    s.check_bogus_field_returns_error(url, 'name', s.random_string(129), None, 'label')
    s.check_bogus_field_returns_error(url, 'name', [], None, 'label')
    s.check_bogus_field_returns_error(url, 'name', {}, None, 'label')
    s.check_bogus_field_returns_error(url, 'type', 123)
    s.check_bogus_field_returns_error(url, 'type', 'invalid')
    s.check_bogus_field_returns_error(url, 'type', True)
    s.check_bogus_field_returns_error(url, 'type', None)
    s.check_bogus_field_returns_error(url, 'type', [])
    s.check_bogus_field_returns_error(url, 'type', {})
    s.check_bogus_field_returns_error(url, 'description', 1234)
    s.check_bogus_field_returns_error(url, 'description', [])
    s.check_bogus_field_returns_error(url, 'description', {})
    s.check_bogus_field_returns_error(url, 'enabled', 'invalid')
    s.check_bogus_field_returns_error(url, 'enabled', None)
    s.check_bogus_field_returns_error(url, 'enabled', [])
    s.check_bogus_field_returns_error(url, 'enabled', {})
    s.check_bogus_field_returns_error(url, 'user_ranges', 123)
    s.check_bogus_field_returns_error(url, 'user_ranges', 'invalid')
    s.check_bogus_field_returns_error(url, 'user_ranges', True)
    s.check_bogus_field_returns_error(url, 'user_ranges', None)
    s.check_bogus_field_returns_error(url, 'user_ranges', {})
    s.check_bogus_field_returns_error(url, 'user_ranges', ['1234'])
    s.check_bogus_field_returns_error(url, 'user_ranges', [{'end': '1234'}])
    s.check_bogus_field_returns_error(url, 'user_ranges', [{'start': None}])
    s.check_bogus_field_returns_error(
        url, 'user_ranges', [{'start': '60', 'end': '50'}]
    )
    s.check_bogus_field_returns_error(
        url, 'user_ranges', [{'start': '50', 'end': '060'}]
    )
    s.check_bogus_field_returns_error(url, 'user_ranges', [{'start': 'invalid'}])
    s.check_bogus_field_returns_error(url, 'group_ranges', 123)
    s.check_bogus_field_returns_error(url, 'group_ranges', 'invalid')
    s.check_bogus_field_returns_error(url, 'group_ranges', True)
    s.check_bogus_field_returns_error(url, 'group_ranges', None)
    s.check_bogus_field_returns_error(url, 'group_ranges', {})
    s.check_bogus_field_returns_error(url, 'group_ranges', ['1234'])
    s.check_bogus_field_returns_error(url, 'group_ranges', [{'end': '1234'}])
    s.check_bogus_field_returns_error(url, 'group_ranges', [{'start': None}])
    s.check_bogus_field_returns_error(
        url, 'group_ranges', [{'start': '60', 'end': '50'}]
    )
    s.check_bogus_field_returns_error(
        url, 'group_ranges', [{'start': '50', 'end': '060'}]
    )
    s.check_bogus_field_returns_error(url, 'group_ranges', [{'start': 'invalid'}])
    s.check_bogus_field_returns_error(url, 'queue_ranges', 123)
    s.check_bogus_field_returns_error(url, 'queue_ranges', 'invalid')
    s.check_bogus_field_returns_error(url, 'queue_ranges', True)
    s.check_bogus_field_returns_error(url, 'queue_ranges', None)
    s.check_bogus_field_returns_error(url, 'queue_ranges', {})
    s.check_bogus_field_returns_error(url, 'queue_ranges', ['1234'])
    s.check_bogus_field_returns_error(url, 'queue_ranges', [{'end': '1234'}])
    s.check_bogus_field_returns_error(url, 'queue_ranges', [{'start': None}])
    s.check_bogus_field_returns_error(
        url, 'queue_ranges', [{'start': '60', 'end': '50'}]
    )
    s.check_bogus_field_returns_error(
        url, 'queue_ranges', [{'start': '50', 'end': '060'}]
    )
    s.check_bogus_field_returns_error(url, 'queue_ranges', [{'start': 'invalid'}])
    s.check_bogus_field_returns_error(url, 'conference_room_ranges', 123)
    s.check_bogus_field_returns_error(url, 'conference_room_ranges', 'invalid')
    s.check_bogus_field_returns_error(url, 'conference_room_ranges', True)
    s.check_bogus_field_returns_error(url, 'conference_room_ranges', None)
    s.check_bogus_field_returns_error(url, 'conference_room_ranges', {})
    s.check_bogus_field_returns_error(url, 'conference_room_ranges', ['1234'])
    s.check_bogus_field_returns_error(url, 'conference_room_ranges', [{'end': '1234'}])
    s.check_bogus_field_returns_error(url, 'conference_room_ranges', [{'start': None}])
    s.check_bogus_field_returns_error(
        url, 'conference_room_ranges', [{'start': '60', 'end': '50'}]
    )
    s.check_bogus_field_returns_error(
        url, 'conference_room_ranges', [{'start': '50', 'end': '060'}]
    )
    s.check_bogus_field_returns_error(
        url, 'conference_room_ranges', [{'start': 'invalid'}]
    )
    s.check_bogus_field_returns_error(url, 'incall_ranges', 123)
    s.check_bogus_field_returns_error(url, 'incall_ranges', 'invalid')
    s.check_bogus_field_returns_error(url, 'incall_ranges', True)
    s.check_bogus_field_returns_error(url, 'incall_ranges', None)
    s.check_bogus_field_returns_error(url, 'incall_ranges', {})
    s.check_bogus_field_returns_error(url, 'incall_ranges', ['1234'])
    s.check_bogus_field_returns_error(url, 'incall_ranges', [{'end': '1234'}])
    s.check_bogus_field_returns_error(url, 'incall_ranges', [{'start': None}])
    s.check_bogus_field_returns_error(
        url, 'incall_ranges', [{'start': '60', 'end': '50'}]
    )
    s.check_bogus_field_returns_error(
        url, 'incall_ranges', [{'start': '50', 'end': '060'}]
    )
    s.check_bogus_field_returns_error(url, 'incall_ranges', [{'start': 'invalid'}])
    s.check_bogus_field_returns_error(
        url, 'incall_ranges', [{'start': '123', 'did_length': None}]
    )


@fixtures.context(
    label='label_search',
    type='internal',
    description='desc_search',
)
@fixtures.context(
    label='hidden',
    type='incall',
    description='hidden',
)
def test_search(context, hidden):
    url = confd.contexts
    searches = {
        'label': 'label_search',
        'type': 'internal',
        'description': 'desc_search',
    }

    for field, term in searches.items():
        check_search(url, context, hidden, field, term)


def check_search(url, context, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, context[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: context[field]})
    assert_that(response.items, has_item(has_entry('id', context['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


@fixtures.context(wazo_tenant=MAIN_TENANT)
@fixtures.context(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.contexts.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

    response = confd.contexts.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

    response = confd.contexts.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.context(label='sort1', description='sort1')
@fixtures.context(label='sort2', description='sort2')
def test_sorting_offset_limit(context1, context2):
    url = confd.contexts.get
    s.check_sorting(url, context1, context2, 'label', 'sort')
    s.check_sorting(url, context1, context2, 'description', 'sort')

    s.check_offset(url, context1, context2, 'label', 'sort')
    s.check_limit(url, context1, context2, 'label', 'sort')


@fixtures.context()
def test_get(context):
    response = confd.contexts(context['id']).get()
    assert_that(
        response.item,
        has_entries(
            id=context['id'],
            name=context['name'],
            label=context['label'],
            type=context['type'],
            user_ranges=context['user_ranges'],
            group_ranges=context['group_ranges'],
            queue_ranges=context['queue_ranges'],
            conference_room_ranges=context['conference_room_ranges'],
            incall_ranges=context['incall_ranges'],
            description=context['description'],
            enabled=context['enabled'],
            tenant_uuid=uuid_(),
            contexts=empty(),
        ),
    )


def test_create_minimal_parameters():
    response = confd.contexts.post(label='MyContext')
    response.assert_created('contexts')

    assert_that(response.item, has_entries(id=not_(empty()), tenant_uuid=MAIN_TENANT))

    confd.contexts(response.item['id']).delete().assert_deleted()


def test_create_out_of_tree_tenant():
    response = confd.contexts.post(
        label='MyContext', wazo_tenant='00000000-0000-0000-0000-000000000000'
    )
    response.assert_status(401)


def test_create_in_authorized_tenant():
    response = confd.contexts.post(label='Context', wazo_tenant=SUB_TENANT)
    response.assert_created('context')

    assert_that(response.item, has_entries(tenant_uuid=SUB_TENANT))


def test_create_all_parameters():
    parameters = {
        'label': 'Context Power',
        'type': 'outcall',
        'user_ranges': [{'start': '1000', 'end': '1999'}],
        'group_ranges': [{'start': '2000', 'end': '2999'}],
        'queue_ranges': [{'start': '3000', 'end': '3999'}],
        'conference_room_ranges': [{'start': '4000', 'end': '4999'}],
        'incall_ranges': [{'start': '1000', 'end': '4999', 'did_length': 2}],
        'description': 'context description',
        'enabled': False,
    }

    response = confd.contexts.post(**parameters)
    response.assert_created('contexts')

    assert_that(response.item, has_entries(tenant_uuid=uuid_(), **parameters))

    confd.contexts(response.item['id']).delete().assert_deleted()


@fixtures.context()
def test_edit_minimal_parameters(context):
    response = confd.contexts(context['id']).put()
    response.assert_updated()


@fixtures.context()
def test_edit_all_parameters(context):
    parameters = {
        'label': 'Context Power',
        'type': 'outcall',
        'user_ranges': [{'start': '1000', 'end': '1999'}],
        'group_ranges': [{'start': '2000', 'end': '2999'}],
        'queue_ranges': [{'start': '3000', 'end': '3999'}],
        'conference_room_ranges': [{'start': '4000', 'end': '4999'}],
        'incall_ranges': [{'start': '1000', 'end': '4999', 'did_length': 2}],
        'description': 'context description',
        'enabled': False,
    }

    response = confd.contexts(context['id']).put(**parameters)
    response.assert_updated()

    response = confd.contexts(context['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.context()
def test_delete(context):
    response = confd.contexts(context['id']).delete()
    response.assert_deleted()
    response = confd.contexts(context['id']).get()
    response.assert_match(404, e.not_found(resource='Context'))


@fixtures.context(label='error')
def test_delete_when_extension_associated(context):
    with fixtures.extension(context=context['name']):
        response = confd.contexts(context['id']).delete()
        response.assert_match(400, e.resource_associated('Context', 'Extension'))


@fixtures.context(label='error')
def test_delete_when_trunk_associated(context):
    with fixtures.trunk(context=context['name']):
        response = confd.contexts(context['id']).delete()
        response.assert_match(400, e.resource_associated('Context', 'Trunk'))


@fixtures.context(label='error')
def test_delete_when_voicemail_associated(context):
    with fixtures.voicemail(context=context['name']):
        response = confd.contexts(context['id']).delete()
        response.assert_match(400, e.resource_associated('Context', 'Voicemail'))


@fixtures.context(label='error')
def test_delete_when_agent_is_logged(context):
    with fixtures.agent_login_status(context=context['name']):
        response = confd.contexts(context['id']).delete()
        response.assert_match(400, e.resource_associated('Context', 'AgentLoginStatus'))


@fixtures.context()
def test_bus_events(context):
    headers = {'tenant_uuid': MAIN_TENANT}

    s.check_event(
        'context_created', headers, confd.contexts.post, {'name': 'bus_event'}
    )
    s.check_event('context_edited', headers, confd.contexts(context['id']).put)
    s.check_event('context_deleted', headers, confd.contexts(context['id']).delete)


def test_create_contexts_parallel():
    def create_context():
        return confd.contexts.post(label='MyContext', wazo_tenant=DELETED_TENANT)

    # create tenants (including DELETED_TENANT) in wazo-auth
    BaseIntegrationTest.mock_auth.set_tenants(*ALL_TENANTS)

    # check DELETED_TENANT does not exist in wazo-confd (not yet created)
    response = confd.tenants(DELETED_TENANT).get(wazo_tenant=MAIN_TENANT)
    response.assert_status(404)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for i in range(5):
            futures.append(executor.submit(create_context))

        for future in concurrent.futures.as_completed(futures):
            response = future.result()
            response.assert_status(201)

    # check if tenant is created now (it has been created during the context creation)
    response = confd.tenants(DELETED_TENANT).get(wazo_tenant=MAIN_TENANT)
    response.assert_status(200)
