# Copyright 2020-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from contextlib import ExitStack, contextmanager
from typing import Dict

from hamcrest import all_of, assert_that, has_entries, has_items, has_key, not_
from sqlalchemy.sql import text
from wazo_test_helpers import until

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers.bus import BusClient
from ..helpers.config import (
    ALL_TENANTS,
    DEFAULT_TENANTS,
    DELETED_TENANT,
    MAIN_TENANT,
    SUB_TENANT,
    gen_group_exten,
    gen_line_exten,
)
from ..helpers.database import DatabaseQueries
from . import BaseIntegrationTest, confd, db


def test_get():
    response = confd.tenants(MAIN_TENANT).get()
    assert_that(
        response.item,
        all_of(
            has_entries(uuid=MAIN_TENANT),
            has_key('sip_templates_generated'),
            has_key('global_sip_template_uuid'),
            has_key('webrtc_sip_template_uuid'),
            has_key('registration_trunk_sip_template_uuid'),
        ),
    )


@fixtures.trunk(wazo_tenant=SUB_TENANT)  # Note: This creates the tenant in the DB
def test_get_multi_tenant(_):
    response = confd.tenants(MAIN_TENANT).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Tenant'))

    response = confd.tenants(SUB_TENANT).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(uuid=SUB_TENANT))


@fixtures.trunk(wazo_tenant=SUB_TENANT)  # Note: This creates the tenant in the DB
def test_list_multi_tenant(_):
    response = confd.tenants.get(wazo_tenant=MAIN_TENANT)
    assert_that(
        response.items,
        all_of(
            has_items(has_entries(uuid=MAIN_TENANT)),
            not_(has_items(has_entries(uuid=SUB_TENANT))),
        ),
    )

    response = confd.tenants.get(wazo_tenant=SUB_TENANT)
    assert_that(
        response.items,
        all_of(
            has_items(has_entries(uuid=SUB_TENANT)),
            not_(has_items(has_entries(uuid=MAIN_TENANT))),
        ),
    )

    response = confd.tenants.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(
        response.items,
        has_items(has_entries(uuid=MAIN_TENANT), has_entries(uuid=SUB_TENANT)),
    )


def test_tenant_deletion_with_event():
    _reset_tenants()
    tables_rows_count_before_deletion = _count_tables_rows()
    with _create_tenant_ready_for_deletion() as tenant_uuid:
        with BaseIntegrationTest.delete_auth_tenant(tenant_uuid):
            BusClient.send_tenant_deleted(DELETED_TENANT, 'slug2')

            def resources_deleted():
                tables_rows_count_after_deletion = _count_tables_rows()
                diff = _diff_tables_rows(
                    tables_rows_count_before_deletion, tables_rows_count_after_deletion
                )
                assert (
                    len(diff) == 0
                ), f'Some tables are not properly cleaned after tenant deletion: {diff}'

            until.assert_(resources_deleted, tries=5, interval=5)


def test_tenant_deletion_with_sync_db():
    _reset_tenants()
    tables_rows_count_before_deletion = _count_tables_rows()
    with _create_tenant_ready_for_deletion() as tenant_uuid:
        with BaseIntegrationTest.delete_auth_tenant(tenant_uuid):
            BaseIntegrationTest.sync_db()

            def resources_deleted():
                tables_rows_count_after_deletion = _count_tables_rows()
                diff = _diff_tables_rows(
                    tables_rows_count_before_deletion, tables_rows_count_after_deletion
                )
                assert (
                    len(diff) == 0
                ), f'Some tables are not properly cleaned after tenant deletion: {diff}'

            until.assert_(resources_deleted, tries=5, interval=5)


def _reset_tenants():
    BaseIntegrationTest.mock_auth.set_tenants(*DEFAULT_TENANTS)

    for t in DEFAULT_TENANTS:
        BusClient.send_tenant_created(t['uuid'], t['slug'])

    # xivo-manage-db creates a tenant (with a random uuid)
    # sync_db is called now to remove this tenant
    BaseIntegrationTest.sync_db()


def _count_table_rows(queries: DatabaseQueries, table_name: str) -> int:
    query = text(f"SELECT COUNT(*) FROM {table_name};")
    count = queries.connection.execute(query).scalar()
    return count


def _count_tables_rows() -> Dict[str, int]:
    excluded_tables = [
        'agentqueueskill',
        'dialaction',
        'pickupmember',
        'func_key',
        'func_key_dest_custom',
    ]
    with db.queries() as queries:
        query = text(
            "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';"
        )
        result = queries.connection.execute(query)
        table_names = set(row.tablename for row in result)
        tables_counts = {
            table_name: _count_table_rows(queries, table_name)
            for table_name in table_names
            if table_name not in excluded_tables
        }
    return tables_counts


def _diff_tables_rows(before: Dict[str, int], after: Dict[str, int]):
    diff = {
        table_name: {
            'before': before[table_name],
            'after': after[table_name],
        }
        for table_name in set(before) | set(after)
        if before.get(table_name) != after.get(table_name)
    }
    return diff


@contextmanager
def _create_tenant_ready_for_deletion():
    # add the tenant DELETED_TENANT in wazo-auth for the authorization,
    # to be able to create the tenant in wazo-confd
    BaseIntegrationTest.mock_auth.set_tenants(*ALL_TENANTS)

    with ExitStack() as stack:
        user = stack.enter_context(fixtures.user(wazo_tenant=DELETED_TENANT))
        group = stack.enter_context(fixtures.group(wazo_tenant=DELETED_TENANT))
        incall = stack.enter_context(fixtures.incall(wazo_tenant=DELETED_TENANT))
        outcall = stack.enter_context(fixtures.outcall(wazo_tenant=DELETED_TENANT))
        conference = stack.enter_context(
            fixtures.conference(wazo_tenant=DELETED_TENANT)
        )
        paging = stack.enter_context(fixtures.paging(wazo_tenant=DELETED_TENANT))
        parking_lot = stack.enter_context(
            fixtures.parking_lot(wazo_tenant=DELETED_TENANT)
        )
        context = stack.enter_context(
            fixtures.context(label='mycontext', wazo_tenant=DELETED_TENANT)
        )
        stack.enter_context(
            fixtures.funckey_template(
                keys={'1': {'destination': {'type': 'custom', 'exten': '123'}}},
                wazo_tenant=DELETED_TENANT,
            )
        )
        switchboard = stack.enter_context(
            fixtures.switchboard(wazo_tenant=DELETED_TENANT)
        )
        stack.enter_context(fixtures.device(wazo_tenant=DELETED_TENANT))
        queue = stack.enter_context(fixtures.queue(wazo_tenant=DELETED_TENANT))
        trunk_sip = stack.enter_context(fixtures.trunk(wazo_tenant=DELETED_TENANT))
        trunk_iax = stack.enter_context(fixtures.trunk(wazo_tenant=DELETED_TENANT))
        trunk_custom = stack.enter_context(fixtures.trunk(wazo_tenant=DELETED_TENANT))
        user_sip = stack.enter_context(
            fixtures.sip(name='endpoint_sip', wazo_tenant=DELETED_TENANT)
        )
        sip = stack.enter_context(
            fixtures.sip(name='endpoint_sip2', wazo_tenant=DELETED_TENANT)
        )
        iax = stack.enter_context(
            fixtures.iax(name='endpoint_iax', wazo_tenant=DELETED_TENANT)
        )
        custom = stack.enter_context(
            fixtures.custom(interface='endpoint_custom', wazo_tenant=DELETED_TENANT)
        )
        agent = stack.enter_context(
            fixtures.agent(number='5678', wazo_tenant=DELETED_TENANT)
        )
        skill = stack.enter_context(fixtures.skill(wazo_tenant=DELETED_TENANT))
        call_pickup = stack.enter_context(
            fixtures.call_pickup(wazo_tenant=DELETED_TENANT)
        )
        user2 = stack.enter_context(fixtures.user(wazo_tenant=DELETED_TENANT))
        stack.enter_context(
            fixtures.call_permission(
                mode='allow',
                enabled=True,
                extensions=[gen_group_exten()],
                wazo_tenant=DELETED_TENANT,
            )
        )
        stack.enter_context(fixtures.call_filter(wazo_tenant=DELETED_TENANT))
        schedule = stack.enter_context(fixtures.schedule(wazo_tenant=DELETED_TENANT))
        trunk = stack.enter_context(fixtures.trunk(wazo_tenant=DELETED_TENANT))
        stack.enter_context(
            fixtures.ivr(
                choices=[{'exten': gen_group_exten(), 'destination': {'type': 'none'}}],
                wazo_tenant=DELETED_TENANT,
            )
        )

        # dest conference function key
        confd.users(user['uuid']).funckeys('1').put(
            {
                'destination': {
                    'type': 'conference',
                    'conference_id': conference['id'],
                }
            }
        )

        # dest paging function key
        confd.users(user['uuid']).funckeys('2').put(
            {
                'destination': {
                    'type': 'paging',
                    'paging_id': paging['id'],
                }
            }
        )

        # dest park position function key
        confd.users(user['uuid']).funckeys('3').put(
            {
                'destination': {
                    'type': 'park_position',
                    'parking_lot_id': parking_lot['id'],
                    'position': '701',
                }
            }
        )

        # dest forward function key
        confd.users(user['uuid']).funckeys('4').put(
            {
                'destination': {
                    'type': 'forward',
                    'exten': '1234',
                }
            }
        )

        # dest agent function key
        confd.users(user['uuid']).funckeys('6').put(
            {
                'destination': {
                    'type': 'agent',
                    'agent_id': agent['id'],
                    'action': 'toggle',
                }
            }
        )

        voicemail = stack.enter_context(
            fixtures.voicemail(context=context['name'], wazo_tenant=DELETED_TENANT)
        )
        line = stack.enter_context(
            fixtures.line_sip(
                context={'name': context['name']}, wazo_tenant=DELETED_TENANT
            )
        )
        group_extension = stack.enter_context(
            fixtures.extension(exten=gen_group_exten(), context=context['name'])
        )
        incall_extension = stack.enter_context(
            fixtures.extension(exten=gen_line_exten(), context=context['name'])
        )
        outcall_extension = stack.enter_context(
            fixtures.extension(exten=gen_line_exten(), context=context['name'])
        )
        stack.enter_context(
            fixtures.funckey_template(
                keys={
                    '1': {
                        'destination': {
                            'type': 'conference',
                            'conference_id': conference['id'],
                        }
                    }
                },
                wazo_tenant=DELETED_TENANT,
            )
        )
        stack.enter_context(a.user_line(user, line, check=False))
        stack.enter_context(a.line_endpoint_sip(line, user_sip, check=False))
        stack.enter_context(a.user_voicemail(user, voicemail, check=False))
        stack.enter_context(a.switchboard_member_user(switchboard, [user], check=False))
        stack.enter_context(a.group_extension(group, group_extension, check=False))
        stack.enter_context(a.user_agent(user, agent, check=False))
        stack.enter_context(a.queue_member_agent(queue, agent, check=False))
        stack.enter_context(a.agent_skill(agent, skill, check=False))
        stack.enter_context(a.incall_extension(incall, incall_extension, check=False))
        stack.enter_context(
            a.outcall_extension(outcall, outcall_extension, check=False)
        )
        stack.enter_context(a.group_member_user(group, user, check=False))
        stack.enter_context(a.trunk_endpoint_sip(trunk_sip, sip, check=False))
        stack.enter_context(a.trunk_endpoint_iax(trunk_iax, iax, check=False))
        stack.enter_context(a.trunk_endpoint_custom(trunk_custom, custom, check=False))
        stack.enter_context(
            a.call_pickup_interceptor_user(call_pickup, user, check=False)
        )
        stack.enter_context(a.call_pickup_target_user(call_pickup, user2, check=False))
        stack.enter_context(a.incall_schedule(incall, schedule, check=False))
        stack.enter_context(a.outcall_trunk(outcall, trunk, check=False))

        yield DELETED_TENANT
