# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import re

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

from . import confd, provd
from ..helpers import (
    associations as a,
    errors as e,
    fixtures,
    helpers as h,
    scenarios as s,
)
from ..helpers.config import (
    CONTEXT,
    EXTEN_OUTSIDE_RANGE,
    gen_conference_exten,
    gen_group_exten,
    gen_queue_exten,
    gen_line_exten,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)

outside_range_regex = re.compile(r"Extension '(\d+)' is outside of range for context '([\w_-]+)'")

FAKE_ID = 999999999


def test_search_errors():
    url = confd.extensions.get
    s.search_error_checks(url)


def test_get_errors():
    url = confd.extensions(FAKE_ID).get
    s.check_resource_not_found(url, 'Extension')


def test_post_errors():
    with fixtures.extension() as extension:
        url = confd.extensions.post
        error_checks(url)



def test_put_errors():
    with fixtures.extension() as extension:
        url = confd.extensions(extension['id']).put
        error_checks(url)



def test_delete_errors():
    url = confd.extensions(FAKE_ID).delete
    s.check_resource_not_found(url, 'Extension')


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'exten', None)
    s.check_bogus_field_returns_error(url, 'exten', True)
    s.check_bogus_field_returns_error(url, 'exten', {})
    s.check_bogus_field_returns_error(url, 'exten', [])
    s.check_bogus_field_returns_error(url, 'exten', '01234567890123456789012345678901234567890')
    s.check_bogus_field_returns_error(url, 'exten', 'ABC123', {'context': CONTEXT})
    s.check_bogus_field_returns_error(url, 'exten', 'XXXX', {'context': CONTEXT})
    s.check_bogus_field_returns_error(url, 'exten', '_+111', {'context': CONTEXT})
    s.check_bogus_field_returns_error(url, 'exten', '_1+111', {'context': 'to-extern'})
    s.check_bogus_field_returns_error(url, 'context', None)
    s.check_bogus_field_returns_error(url, 'context', True)
    s.check_bogus_field_returns_error(url, 'context', {})
    s.check_bogus_field_returns_error(url, 'context', [])


def test_get_multi_tenant():
    with fixtures.context(name='main', wazo_tenant=MAIN_TENANT) as _, fixtures.context(name='sub', wazo_tenant=SUB_TENANT) as __, fixtures.extension(exten='1001', context='main') as in_main, fixtures.extension(exten='1001', context='sub') as in_sub:
        response = confd.extensions(in_main['id']).get(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Extension'))

        response = confd.extensions(in_sub['id']).get(wazo_tenant=SUB_TENANT)
        assert_that(response.item, equal_to(in_sub))



def test_get():
    with fixtures.extension() as extension:
        response = confd.extensions(extension['id']).get()
        assert_that(response.item, has_entries(
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
        ))



def test_create_minimal_parameters():
    exten = h.extension.find_available_exten(CONTEXT)

    response = confd.extensions.post(exten=exten,
                                     context=CONTEXT)
    response.assert_created('extensions')

    assert_that(response.item, has_entries(exten=exten,
                                           context=CONTEXT,
                                           enabled=True,
                                           tenant_uuid=not_(none())))


def test_create_with_enabled_parameter():
    exten = h.extension.find_available_exten(CONTEXT)

    response = confd.extensions.post(exten=exten,
                                     context=CONTEXT,
                                     enabled=False)
    response.assert_created('extensions')

    assert_that(response.item, has_entries(exten=exten,
                                           context=CONTEXT,
                                           enabled=False,
                                           tenant_uuid=not_(none())))


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
    response = confd.extensions.create(exten=exten, context=context)
    response.assert_created('extensions')


def test_create_extension_in_context_with_did_length():
    with fixtures.context(incall_ranges=[{'start': '4185550000', 'end': '4185559999', 'did_length': 4}]) as context:
        response = confd.extensions.create(exten='1000', context=context['name'])
        response.assert_created('extensions')



def test_create_2_extensions_with_same_exten():
    with fixtures.extension() as extension:
        response = confd.extensions.post(context=extension['context'],
                                         exten=extension['exten'])
        response.assert_match(400, e.resource_exists('Extension'))



def test_create_extension_with_fake_context():
    response = confd.extensions.post(exten='1234',
                                     context='fakecontext')
    response.assert_match(400, e.not_found('Context'))


def test_create_pattern():
    response = confd.extensions.post(exten='_XXXX',
                                     context='default')
    response.assert_created('extensions')


def test_create_outcall_pattern():
    response = confd.extensions.post(exten='_+XXXX', context='to-extern')
    response.assert_created('extensions')

    confd.extensions(response.item['id']).delete()


def test_create_2_extensions_same_exten_different_context():
    with fixtures.context() as context:
        exten = h.extension.find_available_exten(CONTEXT)

        response = confd.extensions.post(exten=exten, context=CONTEXT)
        response.assert_created('extensions')

        response = confd.extensions.post(exten=exten, context=context['name'])
        response.assert_created('extensions')



def test_create_multi_tenant():
    with fixtures.context(wazo_tenant=MAIN_TENANT) as in_main:
        response = confd.extensions.post(exten='1001', context=in_main['name'], wazo_tenant=SUB_TENANT)
        response.assert_status(400)



def test_edit_extension_with_same_exten():
    with fixtures.extension(context=CONTEXT) as extension1, fixtures.extension(context=CONTEXT) as extension2:
        response = confd.extensions(extension1['id']).put(exten=extension2['exten'])
        response.assert_status(400)



def test_edit_extension_conference_with_exten_outside_range():
    with fixtures.extension(exten=gen_conference_exten(), context=CONTEXT) as extension, fixtures.conference() as conference:
        with a.conference_extension(conference, extension):
            response = confd.extensions(extension['id']).put(exten=EXTEN_OUTSIDE_RANGE)
            response.assert_match(400, outside_range_regex)


def test_edit_extension_group_with_exten_outside_range():
    with fixtures.extension(exten=gen_group_exten(), context=CONTEXT) as extension, fixtures.group() as group:
        with a.group_extension(group, extension):
            response = confd.extensions(extension['id']).put(exten=EXTEN_OUTSIDE_RANGE)
            response.assert_match(400, outside_range_regex)


def test_edit_extension_queue_with_exten_outside_range():
    with fixtures.extension(exten=gen_queue_exten(), context=CONTEXT) as extension, fixtures.queue() as queue:
        with a.queue_extension(queue, extension):
            response = confd.extensions(extension['id']).put(exten=EXTEN_OUTSIDE_RANGE)
            response.assert_match(400, outside_range_regex)


def test_edit_extension_line_with_exten_outside_range():
    with fixtures.extension(exten=gen_line_exten(), context=CONTEXT) as extension, fixtures.line_sip() as line:
        with a.line_extension(line, extension):
            response = confd.extensions(extension['id']).put(exten=EXTEN_OUTSIDE_RANGE)
            response.assert_match(400, outside_range_regex)


def test_edit_extension_with_fake_context():
    with fixtures.extension() as extension:
        response = confd.extensions(extension['id']).put(exten='1234',
                                                         context='fakecontext')
        response.assert_match(400, e.not_found('Context'))



def test_edit_pattern():
    with fixtures.extension() as extension:
        response = confd.extensions(extension['id']).put(exten='_X21',
                                                         context='default')
        response.assert_updated()



def test_edit_outcall_pattern():
    with fixtures.extension(context='to-extern') as extension:
        response = confd.extensions(extension['id']).put(exten='_+X21')
        response.assert_updated()



def test_edit_multi_tenant():
    with fixtures.context(name='main_ctx', wazo_tenant=MAIN_TENANT) as main_ctx, fixtures.context(name='sub_ctx', wazo_tenant=SUB_TENANT) as _, fixtures.extension(context='main_ctx') as main, fixtures.extension(context='sub_ctx') as sub:
        response = confd.extensions(main['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Extension'))

        response = confd.extensions(sub['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_updated()

        response = confd.extensions(sub['id']).put(context=main_ctx['name'], wazo_tenant=SUB_TENANT)
        response.assert_status(400)



def test_update_required_parameters():
    with fixtures.extension() as extension, fixtures.context() as context:
        exten = h.extension.find_available_exten(context['name'])

        response = confd.extensions(extension['id']).put(exten=exten, context=context['name'])
        response.assert_updated()

        response = confd.extensions(extension['id']).get()
        assert_that(response.item, has_entries(exten=exten, context=context['name']))



def test_update_additional_parameters():
    with fixtures.extension(enabled=True) as extension1:
        response = confd.extensions(extension1['id']).put(enabled=False)
        response.assert_updated()

        response = confd.extensions(extension1['id']).get()
        assert_that(response.item, has_entries(enabled=False))



def test_update_and_multi_tenant():
    with fixtures.context(name='main', wazo_tenant=MAIN_TENANT) as _, fixtures.context(name='sub', wazo_tenant=SUB_TENANT) as __, fixtures.extension(exten='1001', context='main') as in_main, fixtures.extension(exten='1001', context='sub') as in_sub:
        response = confd.extensions(in_main['id']).put(wazo_tenant=SUB_TENANT, enabled=False)
        response.assert_match(404, e.not_found('Extension'))

        response = confd.extensions(in_sub['id']).put(wazo_tenant=SUB_TENANT, enabled=False)
        response.assert_updated()

        response = confd.extensions(in_sub['id']).get()
        assert_that(response.item, has_entries(id=in_sub['id'], enabled=False))

        response = confd.extensions(in_sub['id']).put(context='main', wazo_tenant=SUB_TENANT)
        response.assert_match(400, e.not_found('Context'))



def test_that_changing_tenant_is_not_possible():
    with fixtures.context(name='main', wazo_tenant=MAIN_TENANT) as _, fixtures.context(name='sub', wazo_tenant=SUB_TENANT) as __, fixtures.extension(exten='1001', context='main') as in_main, fixtures.extension(exten='1001', context='sub') as in_sub:
        body = {'exten': '1002', 'context': 'sub'}
        response = confd.extensions(in_main['id']).put(wazo_tenant=MAIN_TENANT, **body)
        response.assert_match(400, e.different_tenant())



def test_edit_extension_then_funckeys_updated():
    with fixtures.user() as user1, fixtures.user() as user2, fixtures.user() as user3, fixtures.line_sip() as line_sip1, fixtures.line_sip() as line_sip2, fixtures.line_sip() as line_sip3, fixtures.extension() as extension1, fixtures.extension() as extension2, fixtures.extension() as extension3, fixtures.device() as device1, fixtures.device() as device2:
        timestamp = datetime.datetime.utcnow()
        with a.line_extension(line_sip1, extension1), a.user_line(user1, line_sip1), a.line_device(line_sip1, device1), \
            a.line_extension(line_sip2, extension2), a.user_line(user2, line_sip2), a.line_device(line_sip2, device2), \
            a.line_extension(line_sip3, extension3), a.user_line(user3, line_sip3):
            device2_updated_count = provd.updated_count(device2['id'], timestamp)

            destination = {'type': 'user', 'user_id': user3['id']}
            confd.users(user1['id']).funckeys(1).put(destination=destination).assert_updated()

            confd.extensions(extension3['id']).put(exten='1033').assert_updated()

            config = provd.configs.get(device1['id'])
            assert_that(config['raw_config']['funckeys']['1']['value'], equal_to('1033'))
            assert_that(provd.updated_count(device2['id'], timestamp), equal_to(device2_updated_count))



def test_edit_extension_with_no_change_device_not_updated():
    with fixtures.user() as user1, fixtures.user() as user2, fixtures.line_sip() as line_sip1, fixtures.line_sip() as line_sip2, fixtures.extension() as extension1, fixtures.extension() as extension2, fixtures.device() as device:
        timestamp = datetime.datetime.utcnow()
        with a.line_extension(line_sip1, extension1), a.user_line(user1, line_sip1), a.line_device(line_sip1, device), \
            a.line_extension(line_sip2, extension2), a.user_line(user2, line_sip2):
            destination = {'type': 'user', 'user_id': user2['id']}
            confd.users(user1['id']).funckeys(1).put(destination=destination).assert_updated()

            device_updated_count = provd.updated_count(device['id'], timestamp)

            confd.extensions(extension2['id']).put(exten=extension2['exten']).assert_updated()

            assert_that(provd.updated_count(device['id'], timestamp), equal_to(device_updated_count))



def test_search_do_not_find_extension_feature():
    with fixtures.extension_feature() as extension:
        response = confd.extensions().get()
        assert_that(response.items, is_not(has_item(has_entries(context=extension['context']))))



def test_search():
    with fixtures.extension(exten='4999', context='default') as extension, fixtures.extension(exten='9999', context='from-extern') as hidden:
        url = confd.extensions
        searches = {'exten': '499',
                    'context': 'fault'}

        for field, term in searches.items():
            check_search(url, extension, hidden, field, term)



def check_search(url, extension, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, extension[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: extension[field]})
    assert_that(response.items, has_item(has_entry('id', extension['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


def test_search_multi_tenant():
    with fixtures.context(name='main', wazo_tenant=MAIN_TENANT) as context, fixtures.context(name='sub', wazo_tenant=SUB_TENANT) as context, fixtures.extension(exten='1001', context='main') as extension, fixtures.extension(exten='1001', context='sub') as extension:
        response = confd.extensions.get(wazo_tenant=SUB_TENANT)
        assert_that(
            response.items,
            all_of(
                not_(has_item(has_entries(context='main'))),
                has_item(has_entries(context='sub')),
            )
        )

        response = confd.extensions.get(wazo_tenant=MAIN_TENANT)
        assert_that(
            response.items,
            has_items(
                has_entries(context='main'),
                not_(has_entries(context='sub')),
            )
        )

        response = confd.extensions.get(recurse=True, wazo_tenant=MAIN_TENANT)
        assert_that(
            response.items,
            has_items(
                has_entries(context='main'),
                has_entries(context='sub'),
            )
        )



def test_sorting_offset_limit():
    with fixtures.extension(exten='9998', context='from-extern') as extension1, fixtures.extension(exten='9999', context='to-extern') as extension2:
        url = confd.extensions.get
        s.check_sorting(url, extension1, extension2, 'exten', '999')
        s.check_sorting(url, extension1, extension2, 'context', 'extern')

        s.check_offset(url, extension1, extension2, 'exten', '999')
        s.check_offset_legacy(url, extension1, extension2, 'exten', '999')

        s.check_limit(url, extension1, extension2, 'exten', '999')



def test_search_extensions_in_context():
    exten1 = h.extension.find_available_exten('default')
    exten2 = h.extension.find_available_exten('from-extern')

    with fixtures.extension(exten=exten1, context='default'), \
            fixtures.extension(exten=exten1, context='from-extern') as extension2, \
            fixtures.extension(exten=exten2, context='from-extern'):

        response = confd.extensions.get(search=exten1, context='from-extern')
        assert_that(response.items, contains(extension2))


def test_search_list_extensions_in_context():
    exten1 = h.extension.find_available_exten('default')
    exten2 = h.extension.find_available_exten('from-extern')

    with fixtures.extension(exten=exten1, context='default'), \
            fixtures.extension(exten=exten1, context='from-extern') as extension2, \
            fixtures.extension(exten=exten2, context='from-extern') as extension3:

        response = confd.extensions.get(context='from-extern')
        assert_that(response.items, contains_inanyorder(extension2, extension3))


def test_search_extensions_by_type():
    with fixtures.extension(context='default') as internal, fixtures.extension(context='from-extern') as incall:
        expected_internal = has_item(has_entries(id=internal['id']))
        expected_incall = has_item(has_entries(id=incall['id']))

        response = confd.extensions.get(type="internal")
        assert_that(response.items, expected_internal)
        assert_that(response.items, not_(expected_incall))

        response = confd.extensions.get(type="incall")
        assert_that(response.items, not_(expected_internal))
        assert_that(response.items, expected_incall)



def test_delete():
    with fixtures.extension() as extension:
        response = confd.extensions(extension['id']).delete()
        response.assert_deleted()



def test_delete_multi_tenant():
    with fixtures.context(name='main', wazo_tenant=MAIN_TENANT) as _, fixtures.context(name='sub', wazo_tenant=SUB_TENANT) as __, fixtures.extension(exten='1001', context='main') as in_main, fixtures.extension(exten='1001', context='sub') as in_sub:
        response = confd.extensions(in_main['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Extension'))

        response = confd.extensions(in_sub['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_deleted()

