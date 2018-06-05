# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    empty,
    has_entries,
    has_entry,
    has_item,
    is_not,
    not_,
)

from . import confd
from ..helpers import (
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.helpers.destination import invalid_destinations, valid_destinations


def test_get_errors():
    fake_queue = confd.queues(999999).get
    yield s.check_resource_not_found, fake_queue, 'Queue'


def test_delete_errors():
    fake_queue = confd.queues(999999).delete
    yield s.check_resource_not_found, fake_queue, 'Queue'


def test_post_errors():
    url = confd.queues.post
    for check in error_checks(url):
        yield check


@fixtures.queue()
def test_put_errors(queue):
    url = confd.queues(queue['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'name', 123
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', None
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', {}
    yield s.check_bogus_field_returns_error, url, 'label', 123
    yield s.check_bogus_field_returns_error, url, 'label', True
    yield s.check_bogus_field_returns_error, url, 'label', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'label', []
    yield s.check_bogus_field_returns_error, url, 'label', {}
    yield s.check_bogus_field_returns_error, url, 'data_quality', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'data_quality', 123
    yield s.check_bogus_field_returns_error, url, 'data_quality', {}
    yield s.check_bogus_field_returns_error, url, 'data_quality', []
    yield s.check_bogus_field_returns_error, url, 'dtmf_hangup_callee_enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'dtmf_hangup_callee_enabled', 123
    yield s.check_bogus_field_returns_error, url, 'dtmf_hangup_callee_enabled', {}
    yield s.check_bogus_field_returns_error, url, 'dtmf_hangup_callee_enabled', []
    yield s.check_bogus_field_returns_error, url, 'dtmf_hangup_caller_enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'dtmf_hangup_caller_enabled', 123
    yield s.check_bogus_field_returns_error, url, 'dtmf_hangup_caller_enabled', {}
    yield s.check_bogus_field_returns_error, url, 'dtmf_hangup_caller_enabled', []
    yield s.check_bogus_field_returns_error, url, 'dtmf_transfer_callee_enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'dtmf_transfer_callee_enabled', 123
    yield s.check_bogus_field_returns_error, url, 'dtmf_transfer_callee_enabled', {}
    yield s.check_bogus_field_returns_error, url, 'dtmf_transfer_callee_enabled', []
    yield s.check_bogus_field_returns_error, url, 'dtmf_transfer_caller_enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'dtmf_transfer_caller_enabled', 123
    yield s.check_bogus_field_returns_error, url, 'dtmf_transfer_caller_enabled', {}
    yield s.check_bogus_field_returns_error, url, 'dtmf_transfer_caller_enabled', []
    yield s.check_bogus_field_returns_error, url, 'dtmf_record_callee_enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'dtmf_record_callee_enabled', 123
    yield s.check_bogus_field_returns_error, url, 'dtmf_record_callee_enabled', {}
    yield s.check_bogus_field_returns_error, url, 'dtmf_record_callee_enabled', []
    yield s.check_bogus_field_returns_error, url, 'dtmf_record_caller_enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'dtmf_record_caller_enabled', 123
    yield s.check_bogus_field_returns_error, url, 'dtmf_record_caller_enabled', {}
    yield s.check_bogus_field_returns_error, url, 'dtmf_record_caller_enabled', []
    yield s.check_bogus_field_returns_error, url, 'retry_on_timeout', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'retry_on_timeout', 123
    yield s.check_bogus_field_returns_error, url, 'retry_on_timeout', {}
    yield s.check_bogus_field_returns_error, url, 'retry_on_timeout', []
    yield s.check_bogus_field_returns_error, url, 'ring_on_hold', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'ring_on_hold', 123
    yield s.check_bogus_field_returns_error, url, 'ring_on_hold', {}
    yield s.check_bogus_field_returns_error, url, 'ring_on_hold', []
    yield s.check_bogus_field_returns_error, url, 'announce_hold_time_on_entry', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'announce_hold_time_on_entry', 123
    yield s.check_bogus_field_returns_error, url, 'announce_hold_time_on_entry', {}
    yield s.check_bogus_field_returns_error, url, 'announce_hold_time_on_entry', []
    yield s.check_bogus_field_returns_error, url, 'ignore_forward', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'ignore_forward', 123
    yield s.check_bogus_field_returns_error, url, 'ignore_forward', {}
    yield s.check_bogus_field_returns_error, url, 'ignore_forward', []
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', 123
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', s.random_string(40)
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', []
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', {}
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', True
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', 1234
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', []
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', {}
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', 1234
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', True
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', s.random_string(81)
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', []
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', {}
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', 123
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', []
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', {}
    yield s.check_bogus_field_returns_error, url, 'timeout', 'ten'
    yield s.check_bogus_field_returns_error, url, 'timeout', -1
    yield s.check_bogus_field_returns_error, url, 'timeout', {}
    yield s.check_bogus_field_returns_error, url, 'timeout', []
    yield s.check_bogus_field_returns_error, url, 'wait_time_threshold', 'ten'
    yield s.check_bogus_field_returns_error, url, 'wait_time_threshold', -1
    yield s.check_bogus_field_returns_error, url, 'wait_time_threshold', {}
    yield s.check_bogus_field_returns_error, url, 'wait_time_threshold', []
    yield s.check_bogus_field_returns_error, url, 'wait_ratio_threshold', 'ten'
    yield s.check_bogus_field_returns_error, url, 'wait_ratio_threshold', -1
    yield s.check_bogus_field_returns_error, url, 'wait_ratio_threshold', {}
    yield s.check_bogus_field_returns_error, url, 'wait_ratio_threshold', []
    yield s.check_bogus_field_returns_error, url, 'options', 123
    yield s.check_bogus_field_returns_error, url, 'options', None
    yield s.check_bogus_field_returns_error, url, 'options', {}
    yield s.check_bogus_field_returns_error, url, 'options', 'string'
    yield s.check_bogus_field_returns_error, url, 'options', [None]
    yield s.check_bogus_field_returns_error, url, 'options', ['string', 'string']
    yield s.check_bogus_field_returns_error, url, 'options', [123, 123]
    yield s.check_bogus_field_returns_error, url, 'options', ['string', 123]
    yield s.check_bogus_field_returns_error, url, 'options', [[]]
    yield s.check_bogus_field_returns_error, url, 'options', [{'key': 'value'}]
    yield s.check_bogus_field_returns_error, url, 'options', [['missing_value']]
    yield s.check_bogus_field_returns_error, url, 'options', [['too', 'much', 'value']]
    yield s.check_bogus_field_returns_error, url, 'options', [['wrong_value', 1234]]
    yield s.check_bogus_field_returns_error, url, 'options', [['none_value', None]]
    yield s.check_bogus_field_returns_error, url, 'enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'enabled', 123
    yield s.check_bogus_field_returns_error, url, 'enabled', {}
    yield s.check_bogus_field_returns_error, url, 'enabled', []

    for destination in invalid_destinations():
        yield s.check_bogus_field_returns_error, url, 'wait_time_destination', destination
    for destination in invalid_destinations():
        yield s.check_bogus_field_returns_error, url, 'wait_ratio_destination', destination

    for check in unique_error_checks(url):
        yield check


@fixtures.queue(name='unique')
@fixtures.group(name='queue_name')
def unique_error_checks(url, queue, group):
    yield s.check_bogus_field_returns_error, url, 'name', queue['name']
    yield s.check_bogus_field_returns_error, url, 'name', group['name']


@fixtures.queue(name='hidden', label='hidden', preprocess_subroutine='hidden')
@fixtures.queue(name='search', label='search', preprocess_subroutine='search')
def test_search(hidden, queue):
    url = confd.queues
    searches = {
        'name': 'search',
        'label': 'search',
        'preprocess_subroutine': 'search',
    }

    for field, term in searches.items():
        yield check_search, url, queue, hidden, field, term


def check_search(url, queue, hidden, field, term):
    response = url.get(search=term)

    expected = has_item(has_entry(field, queue[field]))
    not_expected = has_item(has_entry(field, hidden[field]))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))

    response = url.get(**{field: queue[field]})

    expected = has_item(has_entry('id', queue['id']))
    not_expected = has_item(has_entry('id', hidden['id']))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))


@fixtures.queue(name='sort1', preprocess_subroutine='sort1')
@fixtures.queue(name='sort2', preprocess_subroutine='sort2')
def test_sorting_offset_limit(queue1, queue2):
    url = confd.queues.get
    yield s.check_sorting, url, queue1, queue2, 'name', 'sort'
    yield s.check_sorting, url, queue1, queue2, 'preprocess_subroutine', 'sort'

    yield s.check_offset, url, queue1, queue2, 'name', 'sort'
    yield s.check_offset_legacy, url, queue1, queue2, 'name', 'sort'

    yield s.check_limit, url, queue1, queue2, 'name', 'sort'


@fixtures.queue()
def test_get(queue):
    response = confd.queues(queue['id']).get()
    assert_that(response.item, has_entries(
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
        enabled=queue['enabled'],
        options=not_(empty()),
    ))


def test_create_minimal_parameters():
    response = confd.queues.post(name='MyQueue')
    response.assert_created('queues')

    assert_that(response.item, has_entries(
        id=not_(empty()),
        name='MyQueue',
    ))

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
        'retry_on_timeout': False,
        'ring_on_hold': True,
        'announce_hold_time_on_entry': True,
        'ignore_forward': True,
        'wait_time_threshold': True,
        # 'wait_time_destination': True,
        'wait_ratio_threshold': True,
        # 'wait_ratio_destination': True,
        # 'options': [],
        'caller_id_mode': 'prepend',
        'caller_id_name': 'QUEUE-',
        'timeout': 42,
        'music_on_hold': 'default',
        'preprocess_subroutine': 'subroutine',
        'enabled': False
    }

    response = confd.queues.post(**parameters)
    response.assert_created('queues')

    assert_that(response.item, has_entries(parameters))

    confd.queues(response.item['id']).delete().assert_deleted()


@fixtures.queue()
@fixtures.meetme()
@fixtures.ivr()
@fixtures.group()
@fixtures.outcall()
@fixtures.queue()
@fixtures.switchboard()
@fixtures.user()
@fixtures.voicemail()
@fixtures.conference()
def test_valid_destinations(queue, meetme, ivr, group, outcall, dest_queue, switchboard, user, voicemail, conference):
    for destination in valid_destinations(meetme, ivr, group, outcall, dest_queue,
                                          switchboard, user, voicemail, conference):
        yield create_queue_with_destination, destination
        yield update_queue_with_destination, queue['id'], destination


def create_queue_with_destination(destination):
    response = confd.queues.post(name='queue-destination', wait_time_destination=destination)
    response.assert_created('queue')
    assert_that(response.item, has_entries(wait_time_destination=has_entries(**destination)))

    confd.queues(response.item['id']).delete().assert_deleted()


def update_queue_with_destination(queue_id, destination):
    response = confd.queues(queue_id).put(wait_time_destination=destination)
    response.assert_updated()
    response = confd.queues(queue_id).get()
    assert_that(response.item, has_entries(wait_time_destination=has_entries(**destination)))


@fixtures.queue()
def test_edit_minimal_parameters(queue):
    response = confd.queues(queue['id']).put()
    response.assert_updated()


@fixtures.queue()
def test_edit_all_parameters(queue):
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
        'retry_on_timeout': False,
        'ring_on_hold': True,
        'announce_hold_time_on_entry': True,
        'ignore_forward': True,
        'wait_time_threshold': True,
        'wait_time_destination': {'type': 'none'},
        'wait_ratio_threshold': True,
        'wait_ratio_destination': {'type': 'none'},
        # 'options': [],
        'caller_id_mode': 'prepend',
        'caller_id_name': 'QUEUE-',
        'timeout': 42,
        'music_on_hold': 'default',
        'preprocess_subroutine': 'subroutine',
        'enabled': False
    }

    response = confd.queues(queue['id']).put(**parameters)
    response.assert_updated()

    response = confd.queues(queue['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.queue()
def test_delete(queue):
    response = confd.queues(queue['id']).delete()
    response.assert_deleted()

    response = confd.queues(queue['id']).get()
    response.assert_match(404, e.not_found(resource='Queue'))


@fixtures.queue()
def test_bus_events(queue):
    yield s.check_bus_event, 'config.queue.created', confd.queues.post, {'name': 'bus_event'}
    yield s.check_bus_event, 'config.queue.edited', confd.queues(queue['id']).put
    yield s.check_bus_event, 'config.queue.deleted', confd.queues(queue['id']).delete
