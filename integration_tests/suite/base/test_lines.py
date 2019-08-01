# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from hamcrest import (
    all_of,
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    has_entries,
    has_entry,
    has_item,
    has_items,
    has_length,
    none,
    not_,
)

from . import confd
from ..helpers import (
    associations as a,
    config,
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)


def test_get_errors():
    fake_line_get = confd.lines(999999).get
    s.check_resource_not_found(fake_line_get, 'Line')


def test_post_errors():
    url = confd.lines.post
    error_checks(url)


def test_put_errors():
    with fixtures.line() as line:
        url = confd.lines(line['id']).put
        error_checks(url)

        s.check_bogus_field_returns_error(url, 'provisioning_code', None)
        s.check_bogus_field_returns_error(url, 'position', None)
        s.check_bogus_field_returns_error(url, 'registrar', None)
        s.check_bogus_field_returns_error(url, 'registrar', 'invalidregistrar')



def error_checks(url):
    s.check_bogus_field_returns_error(url, 'context', 123)
    s.check_bogus_field_returns_error(url, 'context', 'undefined')
    s.check_bogus_field_returns_error(url, 'context', '')
    s.check_bogus_field_returns_error(url, 'context', {})
    s.check_bogus_field_returns_error(url, 'context', [])
    s.check_bogus_field_returns_error(url, 'context', None)
    s.check_bogus_field_returns_error(url, 'provisioning_code', 123456)
    s.check_bogus_field_returns_error(url, 'provisioning_code', 'number')
    s.check_bogus_field_returns_error(url, 'provisioning_code', '123')
    s.check_bogus_field_returns_error(url, 'provisioning_code', '1234567')
    s.check_bogus_field_returns_error(url, 'provisioning_code', '')
    s.check_bogus_field_returns_error(url, 'provisioning_code', {})
    s.check_bogus_field_returns_error(url, 'provisioning_code', [])
    s.check_bogus_field_returns_error(url, 'position', 'one')
    s.check_bogus_field_returns_error(url, 'position', '')
    s.check_bogus_field_returns_error(url, 'position', 0)
    s.check_bogus_field_returns_error(url, 'position', {})
    s.check_bogus_field_returns_error(url, 'position', [])
    s.check_bogus_field_returns_error(url, 'registrar', 123)
    s.check_bogus_field_returns_error(url, 'registrar', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'registrar', {})
    s.check_bogus_field_returns_error(url, 'registrar', [])
    s.check_bogus_field_returns_error(url, 'caller_id_name', 123456)
    s.check_bogus_field_returns_error(url, 'caller_id_name', {})
    s.check_bogus_field_returns_error(url, 'caller_id_name', [])
    s.check_bogus_field_returns_error(url, 'caller_id_num', '123ABC')
    s.check_bogus_field_returns_error(url, 'caller_id_num', '')
    s.check_bogus_field_returns_error(url, 'caller_id_num', {})
    s.check_bogus_field_returns_error(url, 'caller_id_num', [])


def test_delete_errors():
    with fixtures.line() as line:
        line_url = confd.lines(line['id'])
        line_url.delete()
        s.check_resource_not_found(line_url.get, 'Line')



def test_get():
    with fixtures.line(context=config.CONTEXT) as line:
        response = confd.lines(line['id']).get()
        assert_that(
            response.item,
            has_entries(
                context=config.CONTEXT,
                position=1,
                device_slot=1,
                name=none(),
                protocol=none(),
                device_id=none(),
                caller_id_name=none(),
                caller_id_num=none(),
                registrar='default',
                provisioning_code=has_length(6),
                provisioning_extension=has_length(6),
                endpoint_sip=none(),
                endpoint_sccp=none(),
                endpoint_custom=none(),
                extensions=empty(),
                users=empty(),
            )
        )



def test_get_multi_tenant():
    with fixtures.context(name='main_ctx', wazo_tenant=MAIN_TENANT) as _, fixtures.context(name='sub_ctx', wazo_tenant=SUB_TENANT) as __, fixtures.line(context='main_ctx') as main, fixtures.line(context='sub_ctx') as sub:
        response = confd.lines(main['id']).get(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Line'))

        response = confd.lines(sub['id']).get(wazo_tenant=MAIN_TENANT)
        assert_that(response.item, has_entries(**sub))



def test_search():
    with fixtures.line() as line1, fixtures.line() as line2:
        response = confd.lines.get()
        assert_that(
            response.items,
            has_items(
                has_entry('id', line1['id']),
                has_entry('id', line2['id']),
            )
        )

        response = confd.lines.get(search=line1['provisioning_code'])
        assert_that(
            response.items,
            contains(has_entry('id', line1['id']))
        )



def test_list_multi_tenant():
    with fixtures.context(name='main_ctx', wazo_tenant=MAIN_TENANT) as _, fixtures.context(name='sub_ctx', wazo_tenant=SUB_TENANT) as __, fixtures.line(context='main_ctx') as main, fixtures.line(context='sub_ctx') as sub:
        response = confd.lines.get(wazo_tenant=MAIN_TENANT)
        assert_that(
            response.items,
            all_of(has_item(main), not_(has_item(sub))),
        )

        response = confd.lines.get(wazo_tenant=SUB_TENANT)
        assert_that(
            response.items,
            all_of(has_item(sub), not_(has_item(main))),
        )

        response = confd.lines.get(wazo_tenant=MAIN_TENANT, recurse=True)
        assert_that(
            response.items,
            has_items(main, sub),
        )



def test_create_line_with_fake_context():
    response = confd.lines.post(context='fakecontext')
    response.assert_match(400, e.not_found('Context'))


def test_create_line_with_minimal_parameters():
    response = confd.lines.post(context=config.CONTEXT)

    response.assert_created('lines')
    assert_that(
        response.item,
        has_entries(
            context=config.CONTEXT,
            position=1,
            device_slot=1,
            name=none(),
            protocol=none(),
            device_id=none(),
            caller_id_name=none(),
            caller_id_num=none(),
            registrar='default',
            provisioning_code=has_length(6),
            provisioning_extension=has_length(6),
            tenant_uuid=MAIN_TENANT,
        )
    )


def test_create_line_with_all_parameters():
    with fixtures.registrar() as registrar:
        response = confd.lines.post(
            context=config.CONTEXT,
            position=2,
            registrar=registrar['id'],
            provisioning_code="887865",
        )

        assert_that(
            response.item,
            has_entries(
                context=config.CONTEXT,
                position=2,
                device_slot=2,
                name=none(),
                protocol=none(),
                device_id=none(),
                caller_id_name=none(),
                caller_id_num=none(),
                registrar=registrar['id'],
                provisioning_code="887865",
                provisioning_extension="887865",
                tenant_uuid=MAIN_TENANT,
            )
        )



def test_create_line_with_caller_id_raises_error():
    response = confd.lines.post(
        context=config.CONTEXT,
        caller_id_name="Jôhn Smîth",
        caller_id_num="1000",
    )

    response.assert_status(400)


def test_create_line_with_provisioning_code_already_taken():
    with fixtures.line(provisioning_code="135246") as line:
        response = confd.lines.post(
            context=config.CONTEXT,
            provisioning_code="135246",
        )
        response.assert_match(400, re.compile("provisioning_code"))



def test_create_multi_tenant():
    with fixtures.context(wazo_tenant=MAIN_TENANT) as in_main:
        response = confd.lines.post(exten='1001', context=in_main['name'], wazo_tenant=SUB_TENANT)
        response.assert_status(400)



def test_update_line_with_fake_context():
    with fixtures.line() as line:
        response = confd.lines(line['id']).put(context='fakecontext')
        response.assert_match(400, e.not_found('Context'))



def test_update_all_parameters_on_line():
    with fixtures.line() as line, fixtures.context() as context, fixtures.registrar() as registrar:
        url = confd.lines(line['id'])

        response = url.put(
            context=context['name'],
            position=2,
            registrar=registrar['id'],
            provisioning_code='243546',
        )
        response.assert_updated()

        response = url.get()
        assert_that(
            response.item,
            has_entries(
                context=context['name'],
                position=2,
                caller_id_name=none(),
                caller_id_num=none(),
                registrar=registrar['id'],
                provisioning_code='243546',
            )
        )



def test_update_caller_id_on_line_without_endpoint_raises_error():
    with fixtures.line() as line:
        response = confd.lines(line['id']).put(caller_id_name="Jôhn Smîth", caller_id_num="1000")
        response.assert_status(400)



def test_when_updating_line_then_values_are_not_overwriten_with_defaults():
    with fixtures.line(position=2) as line:
        url = confd.lines(line['id'])

        response = url.put(provisioning_code="768493")
        response.assert_ok()

        line = url.get().item
        assert_that(line, has_entries(position=2, device_slot=2))



def test_when_line_has_no_endpoint_then_caller_id_can_be_set_to_null():
    with fixtures.line() as line:
        response = confd.lines(line['id']).put(caller_id_name=None, caller_id_num=None)
        response.assert_updated()



def test_edit_multi_tenant():
    with fixtures.context(name='main_ctx', wazo_tenant=MAIN_TENANT) as main_ctx, fixtures.context(name='sub_ctx', wazo_tenant=SUB_TENANT) as _, fixtures.line(context='main_ctx') as main, fixtures.line(context='sub_ctx') as sub:
        response = confd.lines(main['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Line'))

        response = confd.lines(sub['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_updated()

        response = confd.lines(sub['id']).put(context=main_ctx['name'], wazo_tenant=SUB_TENANT)
        response.assert_status(400)



def test_delete_line():
    with fixtures.line() as line:
        response = confd.lines(line['id']).delete()
        response.assert_deleted()



def test_delete_line_then_associatons_are_removed():
    with fixtures.user() as user, fixtures.line_sip() as line1, fixtures.line_sip() as line2, fixtures.extension() as extension, fixtures.device() as device:
        with a.user_line(user, line1, check=False), \
         a.user_line(user, line2, check=False), \
         a.line_extension(line1, extension, check=False), \
         a.line_device(line1, device, check=False):
            response = confd.users(user['id']).lines.get()
            assert_that(
                response.items,
                contains_inanyorder(
                    has_entries(line_id=line1['id'], main_line=True),
                    has_entries(line_id=line2['id'], main_line=False),
                )
            )

            response = confd.devices(device['id']).lines.get()
            assert_that(response.items, not_(empty()))

            response = confd.extensions(extension['id']).lines.get()
            assert_that(response.items, not_(empty()))

            confd.lines(line1['id']).delete()

            response = confd.users(user['id']).lines.get()
            assert_that(
                response.items,
                contains(has_entries(line_id=line2['id'], main_line=True))
            )
            response = confd.devices(device['id']).lines.get()
            assert_that(response.items, empty())

            response = confd.extensions(extension['id']).lines.get()
            assert_that(response.items, empty())
