# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    contains_inanyorder,
    empty,
    has_entries,
    has_entry,
    has_item,
    has_items,
    is_not,
    not_,
)

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import EXTEN_QUEUE_RANGE, MAIN_TENANT, SUB_TENANT
from ..helpers.helpers.destination import invalid_destinations, valid_destinations
from . import confd

ALL_OPTIONS = [
    ['context', 'Default'],
    ['announce', 'MyAnnounce'],
    ['timeout', '42'],
    ['monitor-type', 'mixmonitor'],
    ['monitor-format', 'MyFormat'],
    ['queue-youarenext', 'YouAreNext'],
    ['queue-thereare', 'ThereAre'],
    ['queue-callswaiting', 'callswaiting'],
    ['queue-holdtime', 'HoldTime'],
    ['queue-minutes', 'Minutes'],
    ['queue-seconds', 'Seconds'],
    ['queue-thankyou', 'ThankYou'],
    ['queue-reporthold', 'ReportHold'],
    ['periodic-announce', 'Announce'],
    ['announce-frequency', '43'],
    ['periodic-announce-frequency', '44'],
    ['announce-round-seconds', '45'],
    ['announce-holdtime', 'ABCD'],
    ['retry', '46'],
    ['wrapuptime', '47'],
    ['maxlen', '48'],
    ['servicelevel', '50'],
    ['strategy', 'Random'],
    ['joinempty', 'Join,Empty'],
    ['leavewhenempty', 'Leave,When,Empty'],
    ['ringinuse', 'yes'],
    ['reportholdtime', 'yes'],
    ['memberdelay', '51'],
    ['weight', '52'],
    ['timeoutrestart', 'yes'],
    ['timeoutpriority', 'otherapp'],
    ['autofill', 'no'],
    ['autopause', 'yes'],
    ['setinterfacevar', 'yes'],
    ['setqueueentryvar', 'yes'],
    ['setqueuevar', 'yes'],
    ['membermacro', 'MemberMacro'],
    ['min-announce-frequency', '53'],
    ['random-periodic-announce', 'yes'],
    ['announce-position', 'no'],
    ['announce-position-limit', '54'],
    ['defaultrule', 'DefaultRule'],
]


def test_get_errors():
    fake_queue = confd.queues(999999).get
    s.check_resource_not_found(fake_queue, 'Queue')


def test_delete_errors():
    fake_queue = confd.queues(999999).delete
    s.check_resource_not_found(fake_queue, 'Queue')


@fixtures.user()
def test_post_errors(user):
    url = confd.queues
    error_checks(url.post, user)
    s.check_missing_body_returns_error(url, 'POST')

    s.check_bogus_field_returns_error(url.post, 'name', 123)
    s.check_bogus_field_returns_error(url.post, 'name', 'invalid regex')
    s.check_bogus_field_returns_error(url.post, 'name', 'general')
    s.check_bogus_field_returns_error(url.post, 'name', True)
    s.check_bogus_field_returns_error(url.post, 'name', None)
    s.check_bogus_field_returns_error(url.post, 'name', s.random_string(129))
    s.check_bogus_field_returns_error(url.post, 'name', [])
    s.check_bogus_field_returns_error(url.post, 'name', {})

    unique_error_checks(url.post)


@fixtures.queue()
@fixtures.user()
def test_put_errors(queue, user):
    url = confd.queues(queue['id'])
    error_checks(url.put, user)
    s.check_missing_body_returns_error(url, 'PUT')


def error_checks(url, user):
    s.check_bogus_field_returns_error(url, 'label', 123)
    s.check_bogus_field_returns_error(url, 'label', True)
    s.check_bogus_field_returns_error(url, 'label', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'label', [])
    s.check_bogus_field_returns_error(url, 'label', {})
    s.check_bogus_field_returns_error(url, 'data_quality', 'yeah')
    s.check_bogus_field_returns_error(url, 'data_quality', 123)
    s.check_bogus_field_returns_error(url, 'data_quality', {})
    s.check_bogus_field_returns_error(url, 'data_quality', [])
    s.check_bogus_field_returns_error(url, 'dtmf_hangup_callee_enabled', 'yeah')
    s.check_bogus_field_returns_error(url, 'dtmf_hangup_callee_enabled', 123)
    s.check_bogus_field_returns_error(url, 'dtmf_hangup_callee_enabled', {})
    s.check_bogus_field_returns_error(url, 'dtmf_hangup_callee_enabled', [])
    s.check_bogus_field_returns_error(url, 'dtmf_hangup_caller_enabled', 'yeah')
    s.check_bogus_field_returns_error(url, 'dtmf_hangup_caller_enabled', 123)
    s.check_bogus_field_returns_error(url, 'dtmf_hangup_caller_enabled', {})
    s.check_bogus_field_returns_error(url, 'dtmf_hangup_caller_enabled', [])
    s.check_bogus_field_returns_error(url, 'dtmf_transfer_callee_enabled', 'yeah')
    s.check_bogus_field_returns_error(url, 'dtmf_transfer_callee_enabled', 123)
    s.check_bogus_field_returns_error(url, 'dtmf_transfer_callee_enabled', {})
    s.check_bogus_field_returns_error(url, 'dtmf_transfer_callee_enabled', [])
    s.check_bogus_field_returns_error(url, 'dtmf_transfer_caller_enabled', 'yeah')
    s.check_bogus_field_returns_error(url, 'dtmf_transfer_caller_enabled', 123)
    s.check_bogus_field_returns_error(url, 'dtmf_transfer_caller_enabled', {})
    s.check_bogus_field_returns_error(url, 'dtmf_transfer_caller_enabled', [])
    s.check_bogus_field_returns_error(url, 'dtmf_record_callee_enabled', 'yeah')
    s.check_bogus_field_returns_error(url, 'dtmf_record_callee_enabled', 123)
    s.check_bogus_field_returns_error(url, 'dtmf_record_callee_enabled', {})
    s.check_bogus_field_returns_error(url, 'dtmf_record_callee_enabled', [])
    s.check_bogus_field_returns_error(url, 'dtmf_record_caller_enabled', 'yeah')
    s.check_bogus_field_returns_error(url, 'dtmf_record_caller_enabled', 123)
    s.check_bogus_field_returns_error(url, 'dtmf_record_caller_enabled', {})
    s.check_bogus_field_returns_error(url, 'dtmf_record_caller_enabled', [])
    s.check_bogus_field_returns_error(url, 'dtmf_record_toggle', 'yeah')
    s.check_bogus_field_returns_error(url, 'dtmf_record_toggle', 123)
    s.check_bogus_field_returns_error(url, 'dtmf_record_toggle', {})
    s.check_bogus_field_returns_error(url, 'dtmf_record_toggle', [])
    s.check_bogus_field_returns_error(url, 'retry_on_timeout', 'yeah')
    s.check_bogus_field_returns_error(url, 'retry_on_timeout', 123)
    s.check_bogus_field_returns_error(url, 'retry_on_timeout', {})
    s.check_bogus_field_returns_error(url, 'retry_on_timeout', [])
    s.check_bogus_field_returns_error(url, 'ring_on_hold', 'yeah')
    s.check_bogus_field_returns_error(url, 'ring_on_hold', 123)
    s.check_bogus_field_returns_error(url, 'ring_on_hold', {})
    s.check_bogus_field_returns_error(url, 'ring_on_hold', [])
    s.check_bogus_field_returns_error(url, 'announce_hold_time_on_entry', 'yeah')
    s.check_bogus_field_returns_error(url, 'announce_hold_time_on_entry', 123)
    s.check_bogus_field_returns_error(url, 'announce_hold_time_on_entry', {})
    s.check_bogus_field_returns_error(url, 'announce_hold_time_on_entry', [])
    s.check_bogus_field_returns_error(url, 'ignore_forward', 'yeah')
    s.check_bogus_field_returns_error(url, 'ignore_forward', 123)
    s.check_bogus_field_returns_error(url, 'ignore_forward', {})
    s.check_bogus_field_returns_error(url, 'ignore_forward', [])
    s.check_bogus_field_returns_error(url, 'mark_answered_elsewhere', 'yeah')
    s.check_bogus_field_returns_error(url, 'mark_answered_elsewhere', 123)
    s.check_bogus_field_returns_error(url, 'mark_answered_elsewhere', {})
    s.check_bogus_field_returns_error(url, 'mark_answered_elsewhere', [])
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', 123)
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', s.random_string(80))
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', [])
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', {})
    s.check_bogus_field_returns_error(url, 'caller_id_mode', True)
    s.check_bogus_field_returns_error(url, 'caller_id_mode', 'invalid')
    s.check_bogus_field_returns_error(url, 'caller_id_mode', 1234)
    s.check_bogus_field_returns_error(url, 'caller_id_mode', [])
    s.check_bogus_field_returns_error(url, 'caller_id_mode', {})
    s.check_bogus_field_returns_error(url, 'caller_id_name', 1234)
    s.check_bogus_field_returns_error(url, 'caller_id_name', True)
    s.check_bogus_field_returns_error(url, 'caller_id_name', s.random_string(81))
    s.check_bogus_field_returns_error(url, 'caller_id_name', [])
    s.check_bogus_field_returns_error(url, 'caller_id_name', {})
    s.check_bogus_field_returns_error(url, 'music_on_hold', 123)
    s.check_bogus_field_returns_error(url, 'music_on_hold', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'music_on_hold', [])
    s.check_bogus_field_returns_error(url, 'music_on_hold', {})
    s.check_bogus_field_returns_error(url, 'timeout', 'ten')
    s.check_bogus_field_returns_error(url, 'timeout', -1)
    s.check_bogus_field_returns_error(url, 'timeout', {})
    s.check_bogus_field_returns_error(url, 'timeout', [])
    s.check_bogus_field_returns_error(url, 'wait_time_threshold', 'ten')
    s.check_bogus_field_returns_error(url, 'wait_time_threshold', -1)
    s.check_bogus_field_returns_error(url, 'wait_time_threshold', {})
    s.check_bogus_field_returns_error(url, 'wait_time_threshold', [])
    s.check_bogus_field_returns_error(url, 'wait_ratio_threshold', 'ten')
    s.check_bogus_field_returns_error(url, 'wait_ratio_threshold', -1)
    s.check_bogus_field_returns_error(url, 'wait_ratio_threshold', {})
    s.check_bogus_field_returns_error(url, 'wait_ratio_threshold', [])
    s.check_bogus_field_returns_error(url, 'options', 123)
    s.check_bogus_field_returns_error(url, 'options', None)
    s.check_bogus_field_returns_error(url, 'options', {})
    s.check_bogus_field_returns_error(url, 'options', 'string')
    s.check_bogus_field_returns_error(url, 'options', [None])
    s.check_bogus_field_returns_error(url, 'options', ['string', 'string'])
    s.check_bogus_field_returns_error(url, 'options', [123, 123])
    s.check_bogus_field_returns_error(url, 'options', ['string', 123])
    s.check_bogus_field_returns_error(url, 'options', [[]])
    s.check_bogus_field_returns_error(url, 'options', [{'key': 'value'}])
    s.check_bogus_field_returns_error(url, 'options', [['missing_value']])
    s.check_bogus_field_returns_error(url, 'options', [['too', 'much', 'value']])
    s.check_bogus_field_returns_error(url, 'options', [['wrong_value', 1234]])
    s.check_bogus_field_returns_error(url, 'options', [['none_value', None]])
    s.check_bogus_field_returns_error(url, 'enabled', 'yeah')
    s.check_bogus_field_returns_error(url, 'enabled', 123)
    s.check_bogus_field_returns_error(url, 'enabled', {})
    s.check_bogus_field_returns_error(url, 'enabled', [])

    for destination in invalid_destinations():
        s.check_bogus_field_returns_error(url, 'wait_time_destination', destination)
    s.check_bogus_field_returns_error(
        url,
        'wait_time_destination',
        {
            'type': 'user',
            'user_id': user['id'],
            'moh_uuid': '00000000-0000-0000-0000-000000000000',
        },
        {'name': 'foo'},
        'MOH was not found',
    )

    for destination in invalid_destinations():
        s.check_bogus_field_returns_error(url, 'wait_ratio_destination', destination)
    s.check_bogus_field_returns_error(
        url,
        'wait_ratio_destination',
        {
            'type': 'user',
            'user_id': user['id'],
            'moh_uuid': '00000000-0000-0000-0000-000000000000',
        },
        {'name': 'foo'},
        'MOH was not found',
    )


@fixtures.queue(name='unique')
@fixtures.group(name='queue_name')
def unique_error_checks(url, queue, group):
    s.check_bogus_field_returns_error(url, 'name', queue['name'])
    s.check_bogus_field_returns_error(url, 'name', group['name'])


@fixtures.extension(exten_range=EXTEN_QUEUE_RANGE)
@fixtures.queue(name='hidden', label='hidden', preprocess_subroutine='hidden')
@fixtures.queue(name='search', label='search', preprocess_subroutine='search')
def test_search(extension, hidden, queue):
    url = confd.queues
    searches = {'name': 'search', 'label': 'search', 'preprocess_subroutine': 'search'}

    for field, term in searches.items():
        check_search(url, queue, hidden, field, term)

    searches = {'exten': extension['exten']}
    with a.queue_extension(queue, extension):
        for field, term in searches.items():
            check_relation_search(url, queue, hidden, field, term)


def check_search(url, queue, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, queue[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: queue[field]})
    assert_that(response.items, has_item(has_entry('id', queue['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


def check_relation_search(url, queue, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry('id', queue['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))

    response = url.get(**{field: term})
    assert_that(response.items, has_item(has_entry('id', queue['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


@fixtures.queue(wazo_tenant=MAIN_TENANT)
@fixtures.queue(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.queues.get(wazo_tenant=MAIN_TENANT)
    assert_that(
        response.items,
        all_of(
            has_item(has_entry('id', main['id'])),
            not_(has_item(has_entry('id', sub['id']))),
        ),
    )

    response = confd.queues.get(wazo_tenant=SUB_TENANT)
    assert_that(
        response.items,
        all_of(
            has_item(has_entry('id', sub['id'])),
            not_(has_item(has_entry('id', main['id']))),
        ),
    )

    response = confd.queues.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(
        response.items,
        has_items(has_entry('id', main['id']), has_entry('id', sub['id'])),
    )


@fixtures.queue(name='sort1', preprocess_subroutine='sort1')
@fixtures.queue(name='sort2', preprocess_subroutine='sort2')
def test_sorting_offset_limit(queue1, queue2):
    url = confd.queues.get
    s.check_sorting(url, queue1, queue2, 'name', 'sort')
    s.check_sorting(url, queue1, queue2, 'preprocess_subroutine', 'sort')

    s.check_offset(url, queue1, queue2, 'name', 'sort')
    s.check_limit(url, queue1, queue2, 'name', 'sort')


@fixtures.queue()
def test_get(queue):
    response = confd.queues(queue['id']).get()
    assert_that(
        response.item,
        has_entries(
            id=queue['id'],
            name=queue['name'],
            label=queue['label'],
            data_quality=queue['data_quality'],
            dtmf_hangup_callee_enabled=queue['dtmf_hangup_callee_enabled'],
            dtmf_hangup_caller_enabled=queue['dtmf_hangup_caller_enabled'],
            dtmf_transfer_callee_enabled=queue['dtmf_transfer_callee_enabled'],
            dtmf_transfer_caller_enabled=queue['dtmf_transfer_caller_enabled'],
            dtmf_record_callee_enabled=queue['dtmf_record_callee_enabled'],
            dtmf_record_caller_enabled=queue['dtmf_record_caller_enabled'],
            dtmf_record_toggle=queue['dtmf_record_toggle'],
            retry_on_timeout=queue['retry_on_timeout'],
            ring_on_hold=queue['ring_on_hold'],
            announce_hold_time_on_entry=queue['announce_hold_time_on_entry'],
            ignore_forward=queue['ignore_forward'],
            wait_time_threshold=queue['wait_time_threshold'],
            wait_time_destination=queue['wait_time_destination'],
            wait_ratio_threshold=queue['wait_ratio_threshold'],
            wait_ratio_destination=queue['wait_ratio_destination'],
            caller_id_mode=queue['caller_id_mode'],
            caller_id_name=queue['caller_id_name'],
            timeout=queue['timeout'],
            music_on_hold=queue['music_on_hold'],
            preprocess_subroutine=queue['preprocess_subroutine'],
            mark_answered_elsewhere=queue['mark_answered_elsewhere'],
            enabled=queue['enabled'],
            options=not_(empty()),
            extensions=empty(),
            schedules=empty(),
            members=has_entries(agents=empty(), users=empty()),
        ),
    )


@fixtures.queue(wazo_tenant=MAIN_TENANT)
@fixtures.queue(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.queues(main['id']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Queue'))

    response = confd.queues(sub['id']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(id=sub['id']))


def test_create_minimal_parameters():
    response = confd.queues.post(name='MyQueue')
    response.assert_created('queues')

    assert_that(response.item, has_entries(id=not_(empty()), name='MyQueue'))

    confd.queues(response.item['id']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {
        'name': 'MyQueue',
        'label': 'Label',
        'data_quality': True,
        'dtmf_hangup_callee_enabled': True,
        'dtmf_hangup_caller_enabled': True,
        'dtmf_transfer_callee_enabled': True,
        'dtmf_transfer_caller_enabled': True,
        'dtmf_record_callee_enabled': True,
        'dtmf_record_caller_enabled': True,
        'dtmf_record_toggle': True,
        'retry_on_timeout': False,
        'ring_on_hold': True,
        'announce_hold_time_on_entry': True,
        'ignore_forward': True,
        'wait_time_threshold': 1,
        'wait_time_destination': {'type': 'none'},
        'wait_ratio_threshold': 1,
        'wait_ratio_destination': {'type': 'none'},
        'options': ALL_OPTIONS,
        'caller_id_mode': 'prepend',
        'caller_id_name': 'QUEUE-',
        'timeout': 42,
        'music_on_hold': 'default',
        'preprocess_subroutine': 'subroutine',
        'mark_answered_elsewhere': True,
        'enabled': False,
    }

    response = confd.queues.post(**parameters)
    response.assert_created('queues')

    options = parameters.pop('options')
    assert_that(response.item, has_entries(parameters))
    assert_that(response.item['options'], contains_inanyorder(*options))

    confd.queues(response.item['id']).delete().assert_deleted()


def test_create_multi_tenant():
    response = confd.queues.post(name='MyQueue', wazo_tenant=SUB_TENANT)
    response.assert_created('queues')

    assert_that(response.item, has_entries(tenant_uuid=SUB_TENANT))

    confd.queues(response.item['id']).delete().assert_deleted()


@fixtures.moh(wazo_tenant=MAIN_TENANT)
@fixtures.moh(wazo_tenant=SUB_TENANT)
def test_create_multi_tenant_moh(main_moh, sub_moh):
    parameters = {
        'name': 'MyQueue',
        'music_on_hold': main_moh['name'],
    }
    response = confd.queues.post(**parameters)
    response.assert_created('queues')
    confd.queues(response.item['id']).delete().assert_deleted()

    response = confd.queues.post(**parameters, wazo_tenant=SUB_TENANT)
    response.assert_match(400, e.not_found(resource='MOH'))

    parameters['music_on_hold'] = sub_moh['name']

    response = confd.queues.post(**parameters, wazo_tenant=SUB_TENANT)
    response.assert_created('queues')
    confd.queues(response.item['id']).delete().assert_deleted()

    response = confd.queues.post(**parameters)
    response.assert_match(400, e.not_found(resource='MOH'))


@fixtures.queue()
@fixtures.ivr()
@fixtures.group()
@fixtures.outcall()
@fixtures.queue()
@fixtures.switchboard()
@fixtures.user()
@fixtures.voicemail()
@fixtures.conference()
@fixtures.skill_rule()
@fixtures.application()
@fixtures.moh()
def test_valid_destinations(queue, *destinations):
    for destination in valid_destinations(*destinations):
        create_queue_with_destination(destination)
        update_queue_with_destination(queue['id'], destination)


def create_queue_with_destination(destination):
    response = confd.queues.post(
        name='queue-destination', wait_time_destination=destination
    )
    response.assert_created('queue')
    assert_that(
        response.item, has_entries(wait_time_destination=has_entries(**destination))
    )

    confd.queues(response.item['id']).delete().assert_deleted()


def update_queue_with_destination(queue_id, destination):
    response = confd.queues(queue_id).put(wait_time_destination=destination)
    response.assert_updated()
    response = confd.queues(queue_id).get()
    assert_that(
        response.item, has_entries(wait_time_destination=has_entries(**destination))
    )


@fixtures.queue()
def test_edit_minimal_parameters(queue):
    response = confd.queues(queue['id']).put()
    response.assert_updated()


@fixtures.queue()
def test_edit_all_parameters(queue):
    parameters = {
        'label': 'Label',
        'data_quality': True,
        'dtmf_hangup_callee_enabled': True,
        'dtmf_hangup_caller_enabled': True,
        'dtmf_transfer_callee_enabled': True,
        'dtmf_transfer_caller_enabled': True,
        'dtmf_record_callee_enabled': True,
        'dtmf_record_caller_enabled': True,
        'dtmf_record_toggle': True,
        'retry_on_timeout': False,
        'ring_on_hold': True,
        'announce_hold_time_on_entry': True,
        'ignore_forward': True,
        'wait_time_threshold': 1,
        'wait_time_destination': {'type': 'none'},
        'wait_ratio_threshold': 1,
        'wait_ratio_destination': {'type': 'none'},
        'options': ALL_OPTIONS,
        'caller_id_mode': 'prepend',
        'caller_id_name': 'QUEUE-',
        'timeout': 42,
        'music_on_hold': 'default',
        'preprocess_subroutine': 'subroutine',
        'mark_answered_elsewhere': True,
        'enabled': False,
    }

    response = confd.queues(queue['id']).put(**parameters)
    response.assert_updated()

    response = confd.queues(queue['id']).get()
    options = parameters.pop('options')
    assert_that(response.item, has_entries(parameters))
    assert_that(response.item['options'], contains_inanyorder(*options))


@fixtures.queue(name='OriginalName')
def test_edit_name_unavailable(queue):
    response = confd.queues(queue['id']).put(name='ModifiedName')
    response.assert_updated()

    response = confd.queues(queue['id']).get()
    assert_that(response.item, has_entries(name=queue['name']))


@fixtures.queue(wazo_tenant=MAIN_TENANT)
@fixtures.queue(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.queues(main['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Queue'))

    response = confd.queues(sub['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.queue(wazo_tenant=MAIN_TENANT)
@fixtures.queue(wazo_tenant=SUB_TENANT)
@fixtures.moh(wazo_tenant=MAIN_TENANT)
@fixtures.moh(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant_moh(main, sub, main_moh, sub_moh):
    response = confd.queues(main['id']).put(music_on_hold=sub_moh['name'])
    response.assert_match(400, e.not_found(resource='MOH'))

    response = confd.queues(sub['id']).put(music_on_hold=main_moh['name'])
    response.assert_match(400, e.not_found(resource='MOH'))

    response = confd.queues(main['id']).put(music_on_hold=main_moh['name'])
    response.assert_updated()

    response = confd.queues(sub['id']).put(music_on_hold=sub_moh['name'])
    response.assert_updated()


@fixtures.queue()
def test_delete(queue):
    response = confd.queues(queue['id']).delete()
    response.assert_deleted()

    response = confd.queues(queue['id']).get()
    response.assert_match(404, e.not_found(resource='Queue'))


@fixtures.queue(wazo_tenant=MAIN_TENANT)
@fixtures.queue(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.queues(main['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Queue'))

    response = confd.queues(sub['id']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.queue()
def test_bus_events(queue):
    url = confd.queues(queue['id'])
    headers = {'tenant_uuid': queue['tenant_uuid']}

    s.check_event(
        'queue_created', headers, confd.queues.post, {'name': 'queue_bus_event'}
    )
    s.check_event('queue_edited', headers, url.put)
    s.check_event('queue_deleted', headers, url.delete)
