# Copyright 2020-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from time import sleep

from hamcrest import (
    all_of,
    assert_that,
    has_entries,
    has_items,
    has_key,
    not_,
)
from unittest import TestCase
from sqlalchemy.sql import text
from wazo_test_helpers import until

from . import confd, db, BaseIntegrationTest
from ..helpers import errors as e, fixtures, associations as a
from ..helpers.bus import BusClient
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
    DELETED_TENANT,
    gen_group_exten,
    gen_line_exten,
    ALL_TENANTS,
    DEFAULT_TENANTS,
)


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


class BaseTestTenants(TestCase):
    def count_tables_rows(self):
        tables_counts = {}
        with self.db.queries() as queries:
            query = text(
                "SELECT * FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';"
            )
            result = queries.connection.execute(query)
            for row in result:
                if row.tablename not in self.excluded_tables:
                    query = text(f"SELECT COUNT(*) FROM {row.tablename};")
                    count = queries.connection.execute(query).scalar()
                    tables_counts[row.tablename] = count
        return tables_counts

    def diff(self, after_tables_rows_counts):
        diff = {
            k: {
                'before': self.before_tables_rows_counts[k],
                'after': after_tables_rows_counts[k],
            }
            for k in self.before_tables_rows_counts
            if k in after_tables_rows_counts
            and self.before_tables_rows_counts[k] != after_tables_rows_counts[k]
        }
        return diff


class BaseTestDeleteByEvent(BaseTestTenants):
    def setUp(self):
        self.db = db
        self.excluded_tables = [
            'agentqueueskill',
            'extensions',
            'dialaction',
            'queue',
            'queuemember',
            'pickupmember',
            'queueskillcat',
            'func_key',
            'func_key_dest_custom',
        ]
        self.before_tables_rows_counts = self.count_tables_rows()

    @fixtures.user(wazo_tenant=DELETED_TENANT)
    @fixtures.group(wazo_tenant=DELETED_TENANT)
    @fixtures.incall(wazo_tenant=DELETED_TENANT)
    @fixtures.outcall(wazo_tenant=DELETED_TENANT)
    @fixtures.conference(wazo_tenant=DELETED_TENANT)
    @fixtures.context(label='mycontext', wazo_tenant=DELETED_TENANT)
    @fixtures.funckey_template(
        keys={'1': {'destination': {'type': 'custom', 'exten': '123'}}},
        wazo_tenant=DELETED_TENANT,
    )
    @fixtures.switchboard(wazo_tenant=DELETED_TENANT)
    @fixtures.device(wazo_tenant=DELETED_TENANT)
    @fixtures.queue(wazo_tenant=DELETED_TENANT)
    @fixtures.trunk(wazo_tenant=DELETED_TENANT)
    @fixtures.trunk(wazo_tenant=DELETED_TENANT)
    @fixtures.trunk(wazo_tenant=DELETED_TENANT)
    @fixtures.sip(name='endpoint_sip', wazo_tenant=DELETED_TENANT)
    @fixtures.sip(name='name_search', wazo_tenant=DELETED_TENANT)
    @fixtures.iax(name='name_search', wazo_tenant=DELETED_TENANT)
    @fixtures.custom(interface='name_search', wazo_tenant=DELETED_TENANT)
    @fixtures.agent(number='1234', wazo_tenant=DELETED_TENANT)
    @fixtures.skill(wazo_tenant=DELETED_TENANT, category='mycategory')
    @fixtures.call_pickup(wazo_tenant=DELETED_TENANT)
    @fixtures.user(wazo_tenant=DELETED_TENANT)
    @fixtures.call_permission(
        mode='allow',
        enabled=True,
        extensions=[gen_group_exten()],
        wazo_tenant=DELETED_TENANT)
    @fixtures.call_filter(wazo_tenant=DELETED_TENANT)
    @fixtures.schedule(wazo_tenant=DELETED_TENANT)
    @fixtures.trunk(wazo_tenant=DELETED_TENANT)
    @fixtures.ivr(
        choices=[{'exten': gen_group_exten(), 'destination': {'type': 'none'}}],
        wazo_tenant=DELETED_TENANT)
    def test_delete_tenant_with_many_resources_by_event(
        self,
        user,
        group,
        incall,
        outcall,
        conference,
        context,
        funckey_template,
        switchboard,
        device,
        queue,
        trunk_sip,
        trunk_iax,
        trunk_custom,
        user_sip,
        sip,
        iax,
        custom,
        agent,
        skill,
        call_pickup,
        user2,
        call_permission,
        call_filter,
        schedule,
        trunk,
        ivr,
    ):
        @fixtures.voicemail(context=context['name'], wazo_tenant=DELETED_TENANT)
        @fixtures.line_sip(
            context={'name': context['name']}, wazo_tenant=DELETED_TENANT
        )
        @fixtures.extension(exten=gen_group_exten(), context=context['name'])
        @fixtures.extension(exten=gen_line_exten(), context=context['name'])
        @fixtures.extension(exten=gen_line_exten(), context=context['name'])
        def aux(voicemail, line, group_extension, incall_extension, outcall_extension):
            with (
                a.user_line(user, line, check=False),
                a.line_endpoint_sip(line, user_sip, check=False),
                a.user_voicemail(user, voicemail, check=False),
                a.switchboard_member_user(switchboard, [user], check=False),
                a.group_extension(group, group_extension, check=False),
                a.user_agent(user, agent, check=False),
                a.queue_member_agent(queue, agent, check=False),
                a.agent_skill(agent, skill, check=False),
                a.incall_extension(incall, incall_extension, check=False),
                a.outcall_extension(outcall, outcall_extension, check=False),
                a.group_member_user(group, user, check=False),
                a.trunk_endpoint_sip(trunk_sip, sip, check=False),
                a.trunk_endpoint_iax(trunk_iax, iax, check=False),
                a.trunk_endpoint_custom(trunk_custom, custom, check=False),
                a.call_pickup_interceptor_user(call_pickup, user, check=False),
                a.call_pickup_target_user(call_pickup, user2, check=False),
                a.incall_schedule(incall, schedule, check=False),
                a.outcall_trunk(outcall, trunk, check=False),
            ):
                BusClient.send_tenant_deleted(DELETED_TENANT, 'slug2')

                def resources_deleted():
                    after_deletion_tables_rows_counts = self.count_tables_rows()
                    diff = self.diff(after_deletion_tables_rows_counts)
                    assert (
                        len(diff) == 0
                    ), "Some tables are not properly cleaned after the tenant deletion"

                until.assert_(resources_deleted, tries=5, interval=5)

        aux()


class BaseTestDeleteBySyncDb(BaseTestTenants):
    def setUp(self):
        self.db = db
        self.excluded_tables = [
            'agentqueueskill',
            'extensions',
            'dialaction',
            'queue',
            'queuemember',
            'pickupmember',
            'queueskillcat',
            'func_key',
            'func_key_dest_custom',
        ]

        BaseIntegrationTest.mock_auth.set_tenants(*DEFAULT_TENANTS)

        for t in DEFAULT_TENANTS:
            BusClient.send_tenant_created(t['uuid'], t['slug'])

        # xivo-manage-db creates a tenant (with a random uuid)
        # sync_db is called now to remove this tenant
        BaseIntegrationTest.sync_db()

        # count before the creation of the DELETED_TENANT
        self.before_tables_rows_counts = self.count_tables_rows()

        # add the tenant DELETED_TENANT in wazo-auth for the authorization,
        # to be able to create the tenant in wazo-confd
        BaseIntegrationTest.mock_auth.set_tenants(*ALL_TENANTS)

    @fixtures.user(wazo_tenant=DELETED_TENANT)
    @fixtures.group(wazo_tenant=DELETED_TENANT)
    @fixtures.incall(wazo_tenant=DELETED_TENANT)
    @fixtures.outcall(wazo_tenant=DELETED_TENANT)
    @fixtures.conference(wazo_tenant=DELETED_TENANT)
    @fixtures.context(label='mycontext', wazo_tenant=DELETED_TENANT)
    @fixtures.funckey_template(
        keys={'1': {'destination': {'type': 'custom', 'exten': '123'}}},
        wazo_tenant=DELETED_TENANT,
    )
    @fixtures.switchboard(wazo_tenant=DELETED_TENANT)
    @fixtures.device(wazo_tenant=DELETED_TENANT)
    @fixtures.queue(wazo_tenant=DELETED_TENANT)
    @fixtures.trunk(wazo_tenant=DELETED_TENANT)
    @fixtures.trunk(wazo_tenant=DELETED_TENANT)
    @fixtures.trunk(wazo_tenant=DELETED_TENANT)
    @fixtures.sip(name='endpoint_sip2', wazo_tenant=DELETED_TENANT)
    @fixtures.sip(name='name_search2', wazo_tenant=DELETED_TENANT)
    @fixtures.iax(name='name_search', wazo_tenant=DELETED_TENANT)
    @fixtures.custom(interface='name_search', wazo_tenant=DELETED_TENANT)
    @fixtures.agent(number='1234', wazo_tenant=DELETED_TENANT)
    @fixtures.skill(wazo_tenant=DELETED_TENANT, category='mycategory')
    @fixtures.call_pickup(wazo_tenant=DELETED_TENANT)
    @fixtures.user(wazo_tenant=DELETED_TENANT)
    @fixtures.call_permission(
        mode='allow',
        enabled=True,
        extensions=[gen_group_exten()],
        wazo_tenant=DELETED_TENANT)
    @fixtures.call_filter(wazo_tenant=DELETED_TENANT)
    @fixtures.schedule(wazo_tenant=DELETED_TENANT)
    @fixtures.trunk(wazo_tenant=DELETED_TENANT)
    @fixtures.ivr(choices=[{'exten': gen_group_exten(), 'destination': {'type': 'none'}}], wazo_tenant=DELETED_TENANT)
    def test_delete_tenant_with_many_resources_by_syncdb(
        self,
        user,
        group,
        incall,
        outcall,
        conference,
        context,
        funckey_template,
        switchboard,
        device,
        queue,
        trunk_sip,
        trunk_iax,
        trunk_custom,
        user_sip,
        sip,
        iax,
        custom,
        agent,
        skill,
        call_pickup,
        user2,
        call_permission,
        call_filter,
        schedule,
        trunk,
        ivr,
    ):
        @fixtures.voicemail(context=context['name'], wazo_tenant=DELETED_TENANT)
        @fixtures.line_sip(
            context={'name': context['name']}, wazo_tenant=DELETED_TENANT
        )
        @fixtures.extension(exten=gen_group_exten(), context=context['name'])
        @fixtures.extension(exten=gen_line_exten(), context=context['name'])
        @fixtures.extension(exten=gen_line_exten(), context=context['name'])
        def aux(voicemail, line, group_extension, incall_extension, outcall_extension):
            with (
                a.user_line(user, line, check=False),
                a.line_endpoint_sip(line, user_sip, check=False),
                a.user_voicemail(user, voicemail, check=False),
                a.switchboard_member_user(switchboard, [user], check=False),
                a.group_extension(group, group_extension, check=False),
                a.user_agent(user, agent, check=False),
                a.queue_member_agent(queue, agent, check=False),
                a.agent_skill(agent, skill, check=False),
                a.incall_extension(incall, incall_extension, check=False),
                a.outcall_extension(outcall, outcall_extension, check=False),
                a.group_member_user(group, user, check=False),
                a.trunk_endpoint_sip(trunk_sip, sip, check=False),
                a.trunk_endpoint_iax(trunk_iax, iax, check=False),
                a.trunk_endpoint_custom(trunk_custom, custom, check=False),
                a.call_pickup_interceptor_user(call_pickup, user, check=False),
                a.call_pickup_target_user(call_pickup, user2, check=False),
                a.incall_schedule(incall, schedule, check=False),
                a.outcall_trunk(outcall, trunk, check=False),
            ):
                with BaseIntegrationTest.delete_auth_tenant(DELETED_TENANT):
                    BaseIntegrationTest.sync_db()

                    def resources_deleted():
                        after_deletion_tables_rows_counts = self.count_tables_rows()
                        diff = self.diff(after_deletion_tables_rows_counts)
                        assert (
                            len(diff) == 0
                        ), "Some tables are not properly cleaned after tenant deletion"

                    until.assert_(resources_deleted, tries=5, interval=5)

        aux()
