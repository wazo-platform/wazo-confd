# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import re
from contextlib import ExitStack

from hamcrest import (
    all_of,
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    equal_to,
    has_entries,
    has_entry,
    has_item,
    has_items,
    is_not,
    none,
    not_,
)

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import helpers as h
from ..helpers import scenarios as s
from ..helpers.config import (
    CONTEXT,
    EXTEN_CONFERENCE_RANGE,
    EXTEN_GROUP_RANGE,
    EXTEN_OUTSIDE_RANGE,
    EXTEN_QUEUE_RANGE,
    EXTEN_USER_RANGE,
    MAIN_TENANT,
    SUB_TENANT,
)
from . import BaseIntegrationTest, confd, provd

outside_range_regex = re.compile(
    r"Extension '(\d+)' is outside of range for context '([\w_-]+)'"
)

FAKE_ID = 999999999


def test_search_errors():
    url = confd.extensions.get
    s.search_error_checks(url)


def test_get_errors():
    url = confd.extensions(FAKE_ID).get
    s.check_resource_not_found(url, 'Extension')


@fixtures.extension()
def test_post_errors(extension):
    url = confd.extensions.post
    error_checks(url)
    s.check_missing_body_returns_error(confd.extensions, 'POST')


@fixtures.extension()
def test_put_errors(extension):
    url = confd.extensions(extension['id'])
    error_checks(url.put)
    s.check_missing_body_returns_error(url, 'PUT')


def test_delete_errors():
    url = confd.extensions(FAKE_ID).delete
    s.check_resource_not_found(url, 'Extension')


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'exten', None)
    s.check_bogus_field_returns_error(url, 'exten', True)
    s.check_bogus_field_returns_error(url, 'exten', {})
    s.check_bogus_field_returns_error(url, 'exten', [])
    s.check_bogus_field_returns_error(
        url, 'exten', '01234567890123456789012345678901234567890'
    )
    s.check_bogus_field_returns_error(url, 'exten', 'ABC123', {'context': CONTEXT})
    s.check_bogus_field_returns_error(url, 'exten', 'XXXX', {'context': CONTEXT})
    s.check_bogus_field_returns_error(url, 'exten', '_+111', {'context': CONTEXT})
    s.check_bogus_field_returns_error(url, 'exten', '_1+111', {'context': 'to-extern'})
    s.check_bogus_field_returns_error(url, 'context', None)
    s.check_bogus_field_returns_error(url, 'context', True)
    s.check_bogus_field_returns_error(url, 'context', {})
    s.check_bogus_field_returns_error(url, 'context', [])


@fixtures.context(label='main', wazo_tenant=MAIN_TENANT)
@fixtures.context(label='sub', wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main_ctx, sub_ctx):
    @fixtures.extension(exten='1001', context=main_ctx['name'])
    @fixtures.extension(exten='1001', context=sub_ctx['name'])
    def aux(in_main, in_sub):
        response = confd.extensions(in_main['id']).get(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Extension'))

        response = confd.extensions(in_sub['id']).get(wazo_tenant=SUB_TENANT)
        assert_that(response.item, equal_to(in_sub))

    aux()


@fixtures.extension()
def test_get(extension):
    response = confd.extensions(extension['id']).get()
    assert_that(
        response.item,
        has_entries(
            exten=extension['exten'],
            context=extension['context'],
            enabled=True,
            group=none(),
            queue=none(),
            incall=none(),
            outcall=none(),
            lines=empty(),
            conference=none(),
            parking_lot=none(),
        ),
    )


def test_create_minimal_parameters():
    exten = h.extension.find_available_exten(CONTEXT)

    response = confd.extensions.post(exten=exten, context=CONTEXT)
    response.assert_created('extensions')

    assert_that(
        response.item,
        has_entries(
            exten=exten, context=CONTEXT, enabled=True, tenant_uuid=not_(none())
        ),
    )

    confd.extensions(response.item['id']).delete()


def test_create_with_enabled_parameter():
    exten = h.extension.find_available_exten(CONTEXT)

    response = confd.extensions.post(exten=exten, context=CONTEXT, enabled=False)
    response.assert_created('extensions')

    assert_that(
        response.item,
        has_entries(
            exten=exten, context=CONTEXT, enabled=False, tenant_uuid=not_(none())
        ),
    )

    confd.extensions(response.item['id']).delete()


def test_create_extension_in_different_ranges():
    # user range
    create_in_range('1100', 'default')
    # group range
    create_in_range('2000', 'default')
    # queue range
    create_in_range('3000', 'default')
    # conference range
    create_in_range('4000', 'default')
    # incall range
    create_in_range('3954', 'from-extern')


def create_in_range(exten, context):
    response = confd.extensions.post(exten=exten, context=context)
    response.assert_created('extensions')
    confd.extensions(response.item['id']).delete()


@fixtures.context(
    incall_ranges=[{'start': '4185550000', 'end': '4185559999', 'did_length': 4}]
)
def test_create_extension_in_context_with_did_length(context):
    response = confd.extensions.post(exten='1000', context=context['name'])
    response.assert_created('extensions')
    confd.extensions(response.item['id']).delete()


@fixtures.extension()
def test_create_2_extensions_with_same_exten(extension):
    response = confd.extensions.post(
        context=extension['context'], exten=extension['exten']
    )
    response.assert_match(400, e.resource_exists('Extension'))


def test_create_extension_with_fake_context():
    response = confd.extensions.post(exten='1234', context='fakecontext')
    response.assert_match(400, e.not_found('Context'))


def test_create_pattern():
    response = confd.extensions.post(exten='_XXXX', context='default')
    response.assert_created('extensions')

    confd.extensions(response.item['id']).delete()


def test_create_outcall_pattern():
    response = confd.extensions.post(exten='_+XXXX', context='to-extern')
    response.assert_created('extensions')

    confd.extensions(response.item['id']).delete()


@fixtures.context()
def test_create_2_extensions_same_exten_different_context(context):
    exten = h.extension.find_available_exten(CONTEXT)

    response = confd.extensions.post(exten=exten, context=CONTEXT)
    response.assert_created('extensions')
    confd.extensions(response.item['id']).delete()

    response = confd.extensions.post(exten=exten, context=context['name'])
    response.assert_created('extensions')
    confd.extensions(response.item['id']).delete()


@fixtures.context(wazo_tenant=MAIN_TENANT)
def test_create_multi_tenant(in_main):
    response = confd.extensions.post(
        exten='1001', context=in_main['name'], wazo_tenant=SUB_TENANT
    )
    response.assert_status(400)


@fixtures.extension(context=CONTEXT)
@fixtures.extension(context=CONTEXT)
def test_edit_extension_with_same_exten(extension1, extension2):
    response = confd.extensions(extension1['id']).put(exten=extension2['exten'])
    response.assert_status(400)


@fixtures.extension(exten_range=EXTEN_CONFERENCE_RANGE, context=CONTEXT)
@fixtures.conference()
def test_edit_extension_conference_with_exten_outside_range(extension, conference):
    with a.conference_extension(conference, extension):
        response = confd.extensions(extension['id']).put(exten=EXTEN_OUTSIDE_RANGE)
        response.assert_match(400, outside_range_regex)


@fixtures.extension(exten_range=EXTEN_GROUP_RANGE, context=CONTEXT)
@fixtures.group()
def test_edit_extension_group_with_exten_outside_range(extension, group):
    with a.group_extension(group, extension):
        response = confd.extensions(extension['id']).put(exten=EXTEN_OUTSIDE_RANGE)
        response.assert_match(400, outside_range_regex)


@fixtures.extension(exten_range=EXTEN_QUEUE_RANGE, context=CONTEXT)
@fixtures.queue()
def test_edit_extension_queue_with_exten_outside_range(extension, queue):
    with a.queue_extension(queue, extension):
        response = confd.extensions(extension['id']).put(exten=EXTEN_OUTSIDE_RANGE)
        response.assert_match(400, outside_range_regex)


@fixtures.extension(exten_range=EXTEN_USER_RANGE, context=CONTEXT)
@fixtures.line_sip()
def test_edit_extension_line_with_exten_outside_range(extension, line):
    with a.line_extension(line, extension):
        response = confd.extensions(extension['id']).put(exten=EXTEN_OUTSIDE_RANGE)
        response.assert_match(400, outside_range_regex)


@fixtures.extension()
def test_edit_extension_with_fake_context(extension):
    response = confd.extensions(extension['id']).put(
        exten='1234', context='fakecontext'
    )
    response.assert_match(400, e.not_found('Context'))


@fixtures.extension()
def test_edit_pattern(extension):
    response = confd.extensions(extension['id']).put(exten='_X21', context='default')
    response.assert_updated()


@fixtures.extension(context='to-extern')
def test_edit_outcall_pattern(extension):
    response = confd.extensions(extension['id']).put(exten='_+X21')
    response.assert_updated()


@fixtures.context(label='main_ctx', wazo_tenant=MAIN_TENANT)
@fixtures.context(label='sub_ctx', wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main_ctx, sub_ctx):
    @fixtures.extension(context=main_ctx['name'])
    @fixtures.extension(context=sub_ctx['name'])
    def aux(main, sub):
        response = confd.extensions(main['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Extension'))

        response = confd.extensions(sub['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_updated()

        response = confd.extensions(sub['id']).put(
            context=main_ctx['name'], wazo_tenant=SUB_TENANT
        )
        response.assert_status(400)

    aux()


@fixtures.extension()
@fixtures.context()
def test_update_required_parameters(extension, context):
    exten = h.extension.find_available_exten(context['name'])

    response = confd.extensions(extension['id']).put(
        exten=exten, context=context['name']
    )
    response.assert_updated()

    response = confd.extensions(extension['id']).get()
    assert_that(response.item, has_entries(exten=exten, context=context['name']))


@fixtures.extension(enabled=True)
def test_update_additional_parameters(extension1):
    response = confd.extensions(extension1['id']).put(enabled=False)
    response.assert_updated()

    response = confd.extensions(extension1['id']).get()
    assert_that(response.item, has_entries(enabled=False))


@fixtures.context(label='main', wazo_tenant=MAIN_TENANT)
@fixtures.context(label='sub', wazo_tenant=SUB_TENANT)
def test_update_and_multi_tenant(main_ctx, sub_ctx):
    @fixtures.extension(exten='1001', context=main_ctx['name'])
    @fixtures.extension(exten='1001', context=sub_ctx['name'])
    def aux(in_main, in_sub):
        response = confd.extensions(in_main['id']).put(
            wazo_tenant=SUB_TENANT, enabled=False
        )
        response.assert_match(404, e.not_found('Extension'))

        response = confd.extensions(in_sub['id']).put(
            wazo_tenant=SUB_TENANT, enabled=False
        )
        response.assert_updated()

        response = confd.extensions(in_sub['id']).get()
        assert_that(response.item, has_entries(id=in_sub['id'], enabled=False))

        response = confd.extensions(in_sub['id']).put(
            context=main_ctx['name'], wazo_tenant=SUB_TENANT
        )
        response.assert_match(400, e.not_found('Context'))

    aux()


@fixtures.context(label='main', wazo_tenant=MAIN_TENANT)
@fixtures.context(label='sub', wazo_tenant=SUB_TENANT)
def test_that_changing_tenant_is_not_possible(main_ctx, sub_ctx):
    @fixtures.extension(exten='1001', context=main_ctx['name'])
    @fixtures.extension(exten='1001', context=sub_ctx['name'])
    def aux(in_main, in_sub):
        body = {'exten': '1002', 'context': sub_ctx['name']}
        response = confd.extensions(in_main['id']).put(wazo_tenant=MAIN_TENANT, **body)
        response.assert_match(400, e.different_tenant())

    aux()


@fixtures.user()
@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
@fixtures.line_sip()
@fixtures.extension()
@fixtures.extension()
@fixtures.extension()
@fixtures.device()
@fixtures.device()
def test_edit_extension_then_funckeys_updated(
    user1,
    user2,
    user3,
    line_sip1,
    line_sip2,
    line_sip3,
    extension1,
    extension2,
    extension3,
    device1,
    device2,
):
    timestamp = datetime.datetime.utcnow()
    with ExitStack() as es:
        es.enter_context(a.line_extension(line_sip1, extension1))
        es.enter_context(a.user_line(user1, line_sip1))
        es.enter_context(a.line_device(line_sip1, device1))
        es.enter_context(a.line_extension(line_sip2, extension2))
        es.enter_context(a.user_line(user2, line_sip2))
        es.enter_context(a.line_device(line_sip2, device2))
        es.enter_context(a.line_extension(line_sip3, extension3))
        es.enter_context(a.user_line(user3, line_sip3))

        device2_updated_count = provd.updated_count(
            BaseIntegrationTest, device2['id'], timestamp
        )

        destination = {'type': 'user', 'user_id': user3['id']}
        confd.users(user1['id']).funckeys(1).put(
            destination=destination
        ).assert_updated()

        confd.extensions(extension3['id']).put(exten='1033').assert_updated()

        config = provd.configs.get(device1['id'])
        assert_that(config['raw_config']['funckeys']['1']['value'], equal_to('1033'))
        assert_that(
            provd.updated_count(BaseIntegrationTest, device2['id'], timestamp),
            equal_to(device2_updated_count),
        )


@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
@fixtures.extension()
@fixtures.extension()
@fixtures.device()
def test_edit_extension_with_no_change_device_not_updated(
    user1, user2, line_sip1, line_sip2, extension1, extension2, device
):
    timestamp = datetime.datetime.utcnow()
    with ExitStack() as es:
        es.enter_context(a.line_extension(line_sip1, extension1))
        es.enter_context(a.user_line(user1, line_sip1))
        es.enter_context(a.line_device(line_sip1, device))
        es.enter_context(a.line_extension(line_sip2, extension2))

        destination = {'type': 'user', 'user_id': user2['id']}
        confd.users(user1['id']).funckeys(1).put(
            destination=destination
        ).assert_updated()

        device_updated_count = provd.updated_count(
            BaseIntegrationTest, device['id'], timestamp
        )

        confd.extensions(extension2['id']).put(
            exten=extension2['exten']
        ).assert_updated()

        assert_that(
            provd.updated_count(BaseIntegrationTest, device['id'], timestamp),
            equal_to(device_updated_count),
        )


@fixtures.extension_feature()
def test_search_do_not_find_extension_feature(extension):
    response = confd.extensions().get()
    assert_that(
        response.items, is_not(has_item(has_entries(context=extension['context'])))
    )


@fixtures.extension(exten='4999', context='default')
@fixtures.extension(exten='9999', context='from-extern')
def test_search(extension, hidden):
    url = confd.extensions
    searches = {'exten': '499', 'context': 'fault'}

    for field, term in searches.items():
        check_search(url, extension, hidden, field, term)


def check_search(url, extension, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, extension[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: extension[field]})
    assert_that(response.items, has_item(has_entry('id', extension['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


@fixtures.context(label='main', wazo_tenant=MAIN_TENANT)
@fixtures.context(label='sub', wazo_tenant=SUB_TENANT)
def test_search_multi_tenant(main_ctx, sub_ctx):
    @fixtures.extension(exten='1001', context=main_ctx['name'])
    @fixtures.extension(exten='1001', context=sub_ctx['name'])
    def aux(*_):
        response = confd.extensions.get(wazo_tenant=SUB_TENANT)
        assert_that(
            response.items,
            all_of(
                not_(has_item(has_entries(context=main_ctx['name']))),
                has_item(has_entries(context=sub_ctx['name'])),
            ),
        )

        response = confd.extensions.get(wazo_tenant=MAIN_TENANT)
        assert_that(
            response.items,
            has_items(
                has_entries(context=main_ctx['name']),
                not_(has_entries(context=sub_ctx['name'])),
            ),
        )

        response = confd.extensions.get(recurse=True, wazo_tenant=MAIN_TENANT)
        assert_that(
            response.items,
            has_items(
                has_entries(context=main_ctx['name']),
                has_entries(context=sub_ctx['name']),
            ),
        )

    aux()


@fixtures.extension(exten='9998', context='from-extern')
@fixtures.extension(exten='9999', context='to-extern')
def test_sorting_offset_limit(extension1, extension2):
    url = confd.extensions.get
    s.check_sorting(url, extension1, extension2, 'exten', '999')
    s.check_sorting(url, extension1, extension2, 'context', 'extern')

    s.check_offset(url, extension1, extension2, 'exten', '999')
    s.check_limit(url, extension1, extension2, 'exten', '999')


def test_search_extensions_in_context():
    exten1 = h.extension.find_available_exten('default')
    exten2 = h.extension.find_available_exten('from-extern')
    exten3 = h.extension.find_available_exten('from-extern', exclude=[exten2])

    with ExitStack() as es:
        es.enter_context(fixtures.extension(exten=exten1, context='default'))
        extension2 = es.enter_context(
            fixtures.extension(exten=exten2, context='from-extern')
        )
        es.enter_context(fixtures.extension(exten=exten3, context='from-extern'))

        response = confd.extensions.get(search=exten2, context='from-extern')
        assert_that(response.items, contains(extension2))


def test_search_list_extensions_in_context():
    exten1 = h.extension.find_available_exten('default')
    exten2 = h.extension.find_available_exten('from-extern')
    exten3 = h.extension.find_available_exten('from-extern', exclude=[exten2])

    with ExitStack() as es:
        es.enter_context(fixtures.extension(exten=exten1, context='default'))
        extension2 = es.enter_context(
            fixtures.extension(exten=exten2, context='from-extern')
        )
        extension3 = es.enter_context(
            fixtures.extension(exten=exten3, context='from-extern')
        )

        response = confd.extensions.get(context='from-extern')
        assert_that(response.items, contains_inanyorder(extension2, extension3))


@fixtures.extension(context='default')
@fixtures.extension(context='from-extern')
def test_search_extensions_by_type(internal, incall):
    expected_internal = has_item(has_entries(id=internal['id']))
    expected_incall = has_item(has_entries(id=incall['id']))

    response = confd.extensions.get(type="internal")
    assert_that(response.items, expected_internal)
    assert_that(response.items, not_(expected_incall))

    response = confd.extensions.get(type="incall")
    assert_that(response.items, not_(expected_internal))
    assert_that(response.items, expected_incall)


@fixtures.extension()
@fixtures.extension()
@fixtures.extension()
def test_list_db_requests(*_):
    expected_request_count = 1 + 1  # 1 list + 1 count
    s.check_db_requests(
        BaseIntegrationTest, confd.extensions.get, nb_requests=expected_request_count
    )


@fixtures.extension()
def test_delete(extension):
    response = confd.extensions(extension['id']).delete()
    response.assert_deleted()


@fixtures.context(name='main', wazo_tenant=MAIN_TENANT)
@fixtures.context(name='sub', wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main_ctx, sub_ctx):
    @fixtures.extension(exten='1001', context=main_ctx['name'])
    @fixtures.extension(exten='1001', context=sub_ctx['name'])
    def aux(in_main, in_sub):
        response = confd.extensions(in_main['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Extension'))

        response = confd.extensions(in_sub['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_deleted()

    aux()
