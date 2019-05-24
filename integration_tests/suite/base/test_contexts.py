# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

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
from xivo_test_helpers.hamcrest.uuid_ import uuid_

from . import confd
from ..helpers import (
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)


def test_get_errors():
    fake_context = confd.contexts(999999).get
    yield s.check_resource_not_found, fake_context, 'Context'


def test_delete_errors():
    fake_context = confd.contexts(999999).delete
    yield s.check_resource_not_found, fake_context, 'Context'


def test_post_errors():
    url = confd.contexts.post
    for check in error_checks(url):
        yield check

    yield s.check_bogus_field_returns_error, url, 'name', 123
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', None
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(40)
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', {}

    for check in unique_error_checks(url):
        yield check


@fixtures.context()
def test_put_errors(context):
    url = confd.contexts(context['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'label', 123
    yield s.check_bogus_field_returns_error, url, 'label', True
    yield s.check_bogus_field_returns_error, url, 'label', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'label', []
    yield s.check_bogus_field_returns_error, url, 'label', {}
    yield s.check_bogus_field_returns_error, url, 'type', 123
    yield s.check_bogus_field_returns_error, url, 'type', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'type', True
    yield s.check_bogus_field_returns_error, url, 'type', None
    yield s.check_bogus_field_returns_error, url, 'type', []
    yield s.check_bogus_field_returns_error, url, 'type', {}
    yield s.check_bogus_field_returns_error, url, 'description', 1234
    yield s.check_bogus_field_returns_error, url, 'description', []
    yield s.check_bogus_field_returns_error, url, 'description', {}
    yield s.check_bogus_field_returns_error, url, 'enabled', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'enabled', None
    yield s.check_bogus_field_returns_error, url, 'enabled', []
    yield s.check_bogus_field_returns_error, url, 'enabled', {}
    yield s.check_bogus_field_returns_error, url, 'user_ranges', 123
    yield s.check_bogus_field_returns_error, url, 'user_ranges', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'user_ranges', True
    yield s.check_bogus_field_returns_error, url, 'user_ranges', None
    yield s.check_bogus_field_returns_error, url, 'user_ranges', {}
    yield s.check_bogus_field_returns_error, url, 'user_ranges', ['1234']
    yield s.check_bogus_field_returns_error, url, 'user_ranges', [{'end': '1234'}]
    yield s.check_bogus_field_returns_error, url, 'user_ranges', [{'start': None}]
    yield s.check_bogus_field_returns_error, url, 'user_ranges', [{'start': 'invalid'}]
    yield s.check_bogus_field_returns_error, url, 'group_ranges', 123
    yield s.check_bogus_field_returns_error, url, 'group_ranges', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'group_ranges', True
    yield s.check_bogus_field_returns_error, url, 'group_ranges', None
    yield s.check_bogus_field_returns_error, url, 'group_ranges', {}
    yield s.check_bogus_field_returns_error, url, 'group_ranges', ['1234']
    yield s.check_bogus_field_returns_error, url, 'group_ranges', [{'end': '1234'}]
    yield s.check_bogus_field_returns_error, url, 'group_ranges', [{'start': None}]
    yield s.check_bogus_field_returns_error, url, 'group_ranges', [{'start': 'invalid'}]
    yield s.check_bogus_field_returns_error, url, 'queue_ranges', 123
    yield s.check_bogus_field_returns_error, url, 'queue_ranges', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'queue_ranges', True
    yield s.check_bogus_field_returns_error, url, 'queue_ranges', None
    yield s.check_bogus_field_returns_error, url, 'queue_ranges', {}
    yield s.check_bogus_field_returns_error, url, 'queue_ranges', ['1234']
    yield s.check_bogus_field_returns_error, url, 'queue_ranges', [{'end': '1234'}]
    yield s.check_bogus_field_returns_error, url, 'queue_ranges', [{'start': None}]
    yield s.check_bogus_field_returns_error, url, 'queue_ranges', [{'start': 'invalid'}]
    yield s.check_bogus_field_returns_error, url, 'conference_room_ranges', 123
    yield s.check_bogus_field_returns_error, url, 'conference_room_ranges', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'conference_room_ranges', True
    yield s.check_bogus_field_returns_error, url, 'conference_room_ranges', None
    yield s.check_bogus_field_returns_error, url, 'conference_room_ranges', {}
    yield s.check_bogus_field_returns_error, url, 'conference_room_ranges', ['1234']
    yield s.check_bogus_field_returns_error, url, 'conference_room_ranges', [{'end': '1234'}]
    yield s.check_bogus_field_returns_error, url, 'conference_room_ranges', [{'start': None}]
    yield s.check_bogus_field_returns_error, url, 'conference_room_ranges', [{'start': 'invalid'}]
    yield s.check_bogus_field_returns_error, url, 'incall_ranges', 123
    yield s.check_bogus_field_returns_error, url, 'incall_ranges', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'incall_ranges', True
    yield s.check_bogus_field_returns_error, url, 'incall_ranges', None
    yield s.check_bogus_field_returns_error, url, 'incall_ranges', {}
    yield s.check_bogus_field_returns_error, url, 'incall_ranges', ['1234']
    yield s.check_bogus_field_returns_error, url, 'incall_ranges', [{'end': '1234'}]
    yield s.check_bogus_field_returns_error, url, 'incall_ranges', [{'start': None}]
    yield s.check_bogus_field_returns_error, url, 'incall_ranges', [{'start': 'invalid'}]
    yield s.check_bogus_field_returns_error, url, 'incall_ranges', [{'start': '123', 'did_length': None}]


@fixtures.context(name='unique')
def unique_error_checks(url, context):
    yield s.check_bogus_field_returns_error, url, 'name', context['name']


@fixtures.context(name='search', type='internal', description='desc_search')
@fixtures.context(name='hidden', type='incall', description='hidden')
def test_search(context, hidden):
    url = confd.contexts
    searches = {
        'name': 'search',
        'type': 'internal',
        'description': 'desc_search',
    }

    for field, term in searches.items():
        yield check_search, url, context, hidden, field, term


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


@fixtures.context(name='sort1', description='sort1')
@fixtures.context(name='sort2', description='sort2')
def test_sorting_offset_limit(context1, context2):
    url = confd.contexts.get
    yield s.check_sorting, url, context1, context2, 'name', 'sort'
    yield s.check_sorting, url, context1, context2, 'description', 'sort'

    yield s.check_offset, url, context1, context2, 'name', 'sort'
    yield s.check_offset_legacy, url, context1, context2, 'name', 'sort'

    yield s.check_limit, url, context1, context2, 'name', 'sort'


@fixtures.context()
def test_get(context):
    response = confd.contexts(context['id']).get()
    assert_that(response.item, has_entries(
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
    ))


def test_create_minimal_parameters():
    response = confd.contexts.post(name='MyContext')
    response.assert_created('contexts')

    assert_that(response.item, has_entries(id=not_(empty()), tenant_uuid=MAIN_TENANT))

    confd.contexts(response.item['id']).delete().assert_deleted()


def test_create_out_of_tree_tenant():
    response = confd.contexts.post(name='MyContext', wazo_tenant='00000000-0000-0000-0000-000000000000')
    response.assert_status(401)


def test_create_in_authorized_tenant():
    response = confd.contexts.post(name='ZContext', wazo_tenant=SUB_TENANT)
    response.assert_created('context')

    assert_that(response.item, has_entries(tenant_uuid=SUB_TENANT))


def test_create_all_parameters():
    parameters = {
        'name': 'MyContext',
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


@fixtures.context(name='OriginalName')
def test_edit_name_unavailable(context):
    response = confd.contexts(context['id']).put(name='ModifiedName')
    response.assert_updated()

    response = confd.contexts(context['id']).get()
    assert_that(response.item, has_entries(name=context['name']))


@fixtures.context()
def test_delete(context):
    response = confd.contexts(context['id']).delete()
    response.assert_deleted()
    response = confd.contexts(context['id']).get()
    response.assert_match(404, e.not_found(resource='Context'))


@fixtures.context(name='error')
@fixtures.extension(context='error')
def test_delete_when_extension_associated(context, extension):
    response = confd.contexts(context['id']).delete()
    response.assert_match(400, e.resource_associated('Context', 'Extension'))


@fixtures.context(name='error')
@fixtures.trunk(context='error')
def test_delete_when_trunk_associated(context, trunk):
    response = confd.contexts(context['id']).delete()
    response.assert_match(400, e.resource_associated('Context', 'Trunk'))


@fixtures.context(name='error')
@fixtures.voicemail(context='error')
def test_delete_when_voicemail_associated(context, voicemail):
    response = confd.contexts(context['id']).delete()
    response.assert_match(400, e.resource_associated('Context', 'Voicemail'))


@fixtures.context(name='error')
@fixtures.agent_login_status(context='error')
def test_delete_when_agent_is_logged(context, agent_login_status):
    response = confd.contexts(context['id']).delete()
    response.assert_match(400, e.resource_associated('Context', 'AgentLoginStatus'))


@fixtures.context()
def test_delete_when_sip_general_option_associated(context):
    parameters = {'ordered_options': [], 'options': {'context': context['name']}}
    confd.asterisk.sip.general.put(**parameters).assert_updated()

    response = confd.contexts(context['id']).delete()
    response.assert_match(400, e.resource_associated('Context', 'SIP General'))


@fixtures.context()
def test_bus_events(context):
    yield s.check_bus_event, 'config.contexts.created', confd.contexts.post, {'name': 'bus_event'}
    yield s.check_bus_event, 'config.contexts.edited', confd.contexts(context['id']).put
    yield s.check_bus_event, 'config.contexts.deleted', confd.contexts(context['id']).delete
