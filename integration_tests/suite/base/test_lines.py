# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from hamcrest import (
    all_of,
    assert_that,
    contains_exactly,
    empty,
    has_entries,
    has_entry,
    has_item,
    has_items,
    has_length,
    none,
    not_,
)

from ..helpers import associations as a
from ..helpers import config
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import BaseIntegrationTest, confd


def test_get_errors():
    fake_line_get = confd.lines(999999).get
    s.check_resource_not_found(fake_line_get, 'Line')


def test_post_errors():
    url = confd.lines
    error_checks(url.post)
    s.check_missing_body_returns_error(url, 'POST')


@fixtures.line()
def test_put_errors(line):
    url = confd.lines(line['id'])
    error_checks(url.put)
    s.check_missing_body_returns_error(url, 'PUT')

    s.check_bogus_field_returns_error(url.put, 'provisioning_code', None)
    s.check_bogus_field_returns_error(url.put, 'position', None)
    s.check_bogus_field_returns_error(url.put, 'registrar', None)
    s.check_bogus_field_returns_error(url.put, 'registrar', 'invalidregistrar')


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


@fixtures.line()
def test_delete_errors(line):
    line_url = confd.lines(line['id'])
    line_url.delete()
    s.check_resource_not_found(line_url.get, 'Line')


@fixtures.line(context=config.CONTEXT)
def test_get(line):
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
        ),
    )


@fixtures.context(label='main_ctx', wazo_tenant=MAIN_TENANT)
@fixtures.context(label='sub_ctx', wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main_ctx, sub_ctx):
    with fixtures.line(context=main_ctx['name']) as main:
        with fixtures.line(context=sub_ctx['name']) as sub:
            response = confd.lines(main['id']).get(wazo_tenant=SUB_TENANT)
            response.assert_match(404, e.not_found(resource='Line'))

            response = confd.lines(sub['id']).get(wazo_tenant=MAIN_TENANT)
            assert_that(response.item, has_entries(**sub))


@fixtures.line()
@fixtures.line()
def test_search(line1, line2):
    response = confd.lines.get()
    assert_that(
        response.items,
        has_items(has_entry('id', line1['id']), has_entry('id', line2['id'])),
    )

    response = confd.lines.get(search=line1['provisioning_code'])
    assert_that(response.items, contains_exactly(has_entry('id', line1['id'])))


@fixtures.context(label='main_ctx', wazo_tenant=MAIN_TENANT)
@fixtures.context(label='sub_ctx', wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main_ctx, sub_ctx):
    with fixtures.line(context=main_ctx['name']) as main:
        with fixtures.line(context=sub_ctx['name']) as sub:
            response = confd.lines.get(wazo_tenant=MAIN_TENANT)
            assert_that(response.items, all_of(has_item(main), not_(has_item(sub))))

            response = confd.lines.get(wazo_tenant=SUB_TENANT)
            assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

            response = confd.lines.get(wazo_tenant=MAIN_TENANT, recurse=True)
            assert_that(response.items, has_items(main, sub))


@fixtures.user()
@fixtures.line_sip()
@fixtures.line()
@fixtures.line()
def test_list_db_requests(user1, line1, *_):
    expected_request_count = 1 + 1  # 1 list + 1 count
    with a.user_line(user1, line1):
        s.check_db_requests(
            BaseIntegrationTest, confd.lines.get, nb_requests=expected_request_count
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
        ),
    )


@fixtures.registrar()
def test_create_line_with_all_parameters(registrar):
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
        ),
    )


def test_create_line_with_caller_id_raises_error():
    response = confd.lines.post(
        context=config.CONTEXT, caller_id_name="Jôhn Smîth", caller_id_num="1000"
    )

    response.assert_status(400)


@fixtures.line(provisioning_code="135246")
def test_create_line_with_provisioning_code_already_taken(line):
    response = confd.lines.post(context=config.CONTEXT, provisioning_code="135246")
    response.assert_match(400, re.compile("provisioning_code"))


@fixtures.context(wazo_tenant=MAIN_TENANT)
def test_create_multi_tenant(in_main):
    response = confd.lines.post(
        exten='1001', context=in_main['name'], wazo_tenant=SUB_TENANT
    )
    response.assert_status(400)


@fixtures.line()
def test_update_line_with_fake_context(line):
    response = confd.lines(line['id']).put(context='fakecontext')
    response.assert_match(400, e.not_found('Context'))


@fixtures.line()
@fixtures.context()
@fixtures.registrar()
def test_update_all_parameters_on_line(line, context, registrar):
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
        ),
    )


@fixtures.line()
def test_update_caller_id_on_line_without_endpoint_raises_error(line):
    response = confd.lines(line['id']).put(
        caller_id_name="Jôhn Smîth", caller_id_num="1000"
    )
    response.assert_status(400)


@fixtures.line(position=2)
def test_when_updating_line_then_values_are_not_overwriten_with_defaults(line):
    url = confd.lines(line['id'])

    response = url.put(provisioning_code="768493")
    response.assert_ok()

    line = url.get().item
    assert_that(line, has_entries(position=2, device_slot=2))


@fixtures.line()
def test_when_line_has_no_endpoint_then_caller_id_can_be_set_to_null(line):
    response = confd.lines(line['id']).put(caller_id_name=None, caller_id_num=None)
    response.assert_updated()


@fixtures.context(label='main_ctx', wazo_tenant=MAIN_TENANT)
@fixtures.context(label='sub_ctx', wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main_ctx, sub_ctx):
    with fixtures.line(context=main_ctx['name']) as main:
        with fixtures.line(context=sub_ctx['name']) as sub:
            response = confd.lines(main['id']).put(wazo_tenant=SUB_TENANT)
            response.assert_match(404, e.not_found(resource='Line'))

            response = confd.lines(sub['id']).put(wazo_tenant=MAIN_TENANT)
            response.assert_updated()

            response = confd.lines(sub['id']).put(
                context=main_ctx['name'], wazo_tenant=SUB_TENANT
            )
            response.assert_status(400)


@fixtures.line()
def test_delete_line(line):
    response = confd.lines(line['id']).delete()
    response.assert_deleted()


@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
@fixtures.extension()
@fixtures.device()
def test_delete_line_then_associatons_are_removed(
    user, line1, line2, extension, device
):
    with a.user_line(user, line1, check=False), a.user_line(
        user, line2, check=False
    ), a.line_extension(line1, extension, check=False), a.line_device(
        line1, device, check=False
    ):
        response = confd.users(user['id']).get()
        assert_that(
            response.item,
            has_entries(
                lines=contains_exactly(
                    has_entries(id=line1['id']),
                    has_entries(id=line2['id']),
                )
            ),
        )

        response = confd.devices(device['id']).lines.get()
        assert_that(response.items, not_(empty()))

        response = confd.extensions(extension['id']).get()
        assert_that(response.item, has_entries(lines=not_(empty())))

        confd.lines(line1['id']).delete()

        response = confd.users(user['id']).get()
        assert_that(
            response.item,
            has_entries(lines=contains_exactly(has_entries(id=line2['id']))),
        )

        response = confd.devices(device['id']).lines.get()
        assert_that(response.items, empty())

        response = confd.extensions(extension['id']).get()
        assert_that(response.item, has_entries(lines=empty()))


@fixtures.line_sip()
@fixtures.line_sip()
@fixtures.extension()
def test_recursive_delete_line_with_extension_used_by_other_line_then_extension_not_removed(
    line1, line2, extension
):
    with a.line_extension(line1, extension, check=False), a.line_extension(
        line2, extension, check=False
    ):
        response = confd.lines(line1['id']).delete(recursive=True)
        response.assert_deleted()

        response = confd.extensions(extension['id']).get()
        response.assert_ok()


@fixtures.line_sip()
@fixtures.extension()
def test_recursive_delete_line_with_extension_not_used_by_other_line_then_extension_removed(
    line1, extension
):
    with a.line_extension(line1, extension, check=False):
        response = confd.lines(line1['id']).delete(recursive=True)
        response.assert_deleted()

        response = confd.extensions(extension['id']).get()
        response.assert_status(404)


@fixtures.user()
@fixtures.line_sip()
def test_recursive_delete_line_then_user_associaton_removed(user, line1):
    with a.user_line(user, line1, check=False):
        response = confd.users(user['id']).get()
        assert_that(
            response.item,
            has_entries(
                lines=contains_exactly(
                    has_entries(id=line1['id']),
                )
            ),
        )

        confd.lines(line1['id']).delete(recursive=True)

        response = confd.users(user['id']).get()
        assert_that(response.item, has_entries(lines=empty()))
