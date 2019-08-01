# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
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
from ..helpers.helpers.destination import invalid_destinations, valid_destinations

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


def test_post_errors():
    url = confd.queues.post
    error_checks(url)

    s.check_bogus_field_returns_error(url, 'name', 123)
    s.check_bogus_field_returns_error(url, 'name', 'invalid regex')
    s.check_bogus_field_returns_error(url, 'name', 'general')
    s.check_bogus_field_returns_error(url, 'name', True)
    s.check_bogus_field_returns_error(url, 'name', None)
    s.check_bogus_field_returns_error(url, 'name', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'name', [])
    s.check_bogus_field_returns_error(url, 'name', {})

    unique_error_checks(url)


def test_put_errors():
    with fixtures.queue() as queue:
        url = confd.queues(queue['id']).put
        error_checks(url)



def error_checks(url):
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
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', 123)
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', s.random_string(40))
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
    for destination in invalid_destinations():
        s.check_bogus_field_returns_error(url, 'wait_ratio_destination', destination)


def unique_error_checks(url):
    with fixtures.queue(name='unique') as queue, fixtures.group(name='queue_name') as group:
        s.check_bogus_field_returns_error(url, 'name', queue['name'])
        s.check_bogus_field_returns_error(url, 'name', group['name'])



def test_search():
    with fixtures.queue(name='hidden', label='hidden', preprocess_subroutine='hidden') as hidden, fixtures.queue(name='search', label='search', preprocess_subroutine='search') as queue:
        url = confd.queues
        searches = {
            'name': 'search',
            'label': 'search',
            'preprocess_subroutine': 'search',
        }

        for field, term in searches.items():
            check_search(url, queue, hidden, field, term)



def check_search(url, queue, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, queue[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: queue[field]})
    assert_that(response.items, has_item(has_entry('id', queue['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


def test_list_multi_tenant():
    with fixtures.queue(wazo_tenant=MAIN_TENANT) as main, fixtures.queue(wazo_tenant=SUB_TENANT) as sub:
        response = confd.queues.get(wazo_tenant=MAIN_TENANT)
        assert_that(
            response.items,
            all_of(
                has_item(has_entry('id', main['id'])),
                not_(has_item(has_entry('id', sub['id']))),
            )
        )

        response = confd.queues.get(wazo_tenant=SUB_TENANT)
        assert_that(
            response.items,
            all_of(
                has_item(has_entry('id', sub['id'])),
                not_(has_item(has_entry('id', main['id']))),
            )
        )

        response = confd.queues.get(wazo_tenant=MAIN_TENANT, recurse=True)
        assert_that(
            response.items,
            has_items(has_entry('id', main['id']), has_entry('id', sub['id']))
        )



def test_sorting_offset_limit():
    with fixtures.queue(name='sort1', preprocess_subroutine='sort1') as queue1, fixtures.queue(name='sort2', preprocess_subroutine='sort2') as queue2:
        url = confd.queues.get
        s.check_sorting(url, queue1, queue2, 'name', 'sort')
        s.check_sorting(url, queue1, queue2, 'preprocess_subroutine', 'sort')

        s.check_offset(url, queue1, queue2, 'name', 'sort')
        s.check_offset_legacy(url, queue1, queue2, 'name', 'sort')

        s.check_limit(url, queue1, queue2, 'name', 'sort')



def test_get():
    with fixtures.queue() as queue:
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

            extensions=empty(),
            schedules=empty(),
            members=has_entries(
                agents=empty(),
                users=empty(),
            ),
        ))



def test_get_multi_tenant():
    with fixtures.queue(wazo_tenant=MAIN_TENANT) as main, fixtures.queue(wazo_tenant=SUB_TENANT) as sub:
        response = confd.queues(main['id']).get(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Queue'))

        response = confd.queues(sub['id']).get(wazo_tenant=MAIN_TENANT)
        assert_that(response.item, has_entries(id=sub['id']))



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
        'wait_time_destination': {'type': 'none'},
        'wait_ratio_threshold': True,
        'wait_ratio_destination': {'type': 'none'},
        'options': ALL_OPTIONS,
        'caller_id_mode': 'prepend',
        'caller_id_name': 'QUEUE-',
        'timeout': 42,
        'music_on_hold': 'default',
        'preprocess_subroutine': 'subroutine',
        'enabled': False
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


def test_valid_destinations():
    with fixtures.queue() as queue, \
            fixtures.meetme() as meetme, \
            fixtures.ivr() as ivr, \
            fixtures.group() as group, \
            fixtures.outcall() as outcall, \
            fixtures.queue() as queue2, \
            fixtures.switchboard() as switchboard, \
            fixtures.user() as user, \
            fixtures.voicemail() as voicemail, \
            fixtures.conference() as conference, \
            fixtures.skill_rule() as skill_rule, \
            fixtures.application() as application:
        destinations = (meetme, ivr, group, outcall, queue2, switchboard, user,
                        voicemail, conference, skill_rule, application)
        for destination in valid_destinations(*destinations):
            create_queue_with_destination(destination)
            update_queue_with_destination(queue['id'], destination)


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


def test_edit_minimal_parameters():
    with fixtures.queue() as queue:
        response = confd.queues(queue['id']).put()
        response.assert_updated()



def test_edit_all_parameters():
    with fixtures.queue() as queue:
        parameters = {
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
            'options': ALL_OPTIONS,
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
        options = parameters.pop('options')
        assert_that(response.item, has_entries(parameters))
        assert_that(response.item['options'], contains_inanyorder(*options))



def test_edit_name_unavailable():
    with fixtures.queue(name='OriginalName') as queue:
        response = confd.queues(queue['id']).put(name='ModifiedName')
        response.assert_updated()

        response = confd.queues(queue['id']).get()
        assert_that(response.item, has_entries(name=queue['name']))



def test_edit_multi_tenant():
    with fixtures.queue(wazo_tenant=MAIN_TENANT) as main, fixtures.queue(wazo_tenant=SUB_TENANT) as sub:
        response = confd.queues(main['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Queue'))

        response = confd.queues(sub['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_updated()



def test_delete():
    with fixtures.queue() as queue:
        response = confd.queues(queue['id']).delete()
        response.assert_deleted()

        response = confd.queues(queue['id']).get()
        response.assert_match(404, e.not_found(resource='Queue'))



def test_delete_multi_tenant():
    with fixtures.queue(wazo_tenant=MAIN_TENANT) as main, fixtures.queue(wazo_tenant=SUB_TENANT) as sub:
        response = confd.queues(main['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Queue'))

        response = confd.queues(sub['id']).delete(wazo_tenant=MAIN_TENANT)
        response.assert_deleted()



def test_bus_events():
    with fixtures.queue() as queue:
        s.check_bus_event('config.queue.created', confd.queues.post, {'name': 'queue_bus_event'})
        s.check_bus_event('config.queue.edited', confd.queues(queue['id']).put)
        s.check_bus_event('config.queue.deleted', confd.queues(queue['id']).delete)

