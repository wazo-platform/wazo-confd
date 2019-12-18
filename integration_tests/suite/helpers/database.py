# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from contextlib import contextmanager
from functools import wraps

import sqlalchemy as sa

from sqlalchemy.sql import text


def reset(db):
    def decorated(decorated):
        @wraps(decorated)
        def wrapper(*args, **kwargs):
            db.recreate()
            return decorated(*args, **kwargs)

        return wrapper

    return decorated


class DbHelper:

    TEMPLATE = "xivotemplate"

    @classmethod
    def build(cls, user, password, host, port, db):
        tpl = "postgresql://{user}:{password}@{host}:{port}"
        uri = tpl.format(user=user, password=password, host=host, port=port)
        return cls(uri, db)

    def __init__(self, uri, db):
        self.uri = uri
        self.db = db

    def create_engine(self, db=None, isolate=False):
        db = db or self.db
        uri = "{}/{}".format(self.uri, db)
        if isolate:
            return sa.create_engine(uri, isolation_level='AUTOCOMMIT')
        return sa.create_engine(uri)

    def connect(self, db=None):
        db = db or self.db
        return self.create_engine(db).connect()

    def recreate(self):
        engine = self.create_engine("postgres", isolate=True)
        connection = engine.connect()
        connection.execute(
            """
                           SELECT pg_terminate_backend(pg_stat_activity.pid)
                           FROM pg_stat_activity
                           WHERE pg_stat_activity.datname = '{db}'
                           AND pid <> pg_backend_pid()
                           """.format(
                db=self.db
            )
        )
        connection.execute("DROP DATABASE IF EXISTS {db}".format(db=self.db))
        connection.execute(
            "CREATE DATABASE {db} TEMPLATE {template}".format(
                db=self.db, template=self.TEMPLATE
            )
        )
        connection.close()

    def execute(self, query, **kwargs):
        with self.connect() as connection:
            connection.execute(text(query), **kwargs)

    @contextmanager
    def queries(self):
        with self.connect() as connection:
            yield DatabaseQueries(connection)


class DatabaseQueries:
    def __init__(self, connection):
        self.connection = connection

    def insert_queue(
        self, name='myqueue', number='3000', context='default', tenant_uuid=None
    ):
        queue_query = text(
            """
        INSERT INTO queuefeatures (name, displayname, number, context, tenant_uuid)
        VALUES (:name, :displayname, :number, :context, :tenant_uuid)
        RETURNING id
        """
        )

        queue_id = self.connection.execute(
            queue_query,
            name=name,
            displayname=name,
            number=number,
            context=context,
            tenant_uuid=tenant_uuid,
        ).scalar()

        self.insert_extension(number, context, 'queue', queue_id)

        func_key_id = self.insert_func_key('speeddial', 'queue')
        self.insert_destination('queue', 'queue_id', func_key_id, queue_id)

        return queue_id

    def associate_queue_extension(self, queue_id, extension_id):
        query = text(
            "UPDATE extensions SET type = 'queue', typeval = :queue_id WHERE id = :extension_id"
        )
        self.connection.execute(query, queue_id=queue_id, extension_id=extension_id)

    def dissociate_queue_extension(self, queue_id, extension_id):
        query = text(
            "UPDATE extensions SET type = 'user', typeval = 0 WHERE id = :extension_id"
        )
        self.connection.execute(query, extension_id=extension_id)

    def insert_extension_feature(self, exten='1000', feature='default', enabled=True):
        query = text(
            """
        INSERT INTO extensions
        (exten, context, type, typeval, commented)
        VALUES (
            :exten,
            'xivo-features',
            'extenfeatures',
            :feature,
            :commented
        )
        RETURNING id
        """
        )

        agent_id = self.connection.execute(
            query, exten=exten, feature=feature, commented=1 if not enabled else 0
        ).scalar()

        return agent_id

    def delete_extension_feature(self, extension_id):
        query = text(
            "DELETE FROM extensions WHERE id = :extension_id AND context = 'xivo-features'"
        )
        self.connection.execute(query, extension_id=extension_id)

    def insert_func_key(self, func_key_type, destination_type):
        func_key_query = text(
            """
        INSERT INTO func_key (type_id, destination_type_id)
        VALUES (
        (SELECT id FROM func_key_type WHERE name = :func_key_type),
        (SELECT id FROM func_key_destination_type WHERE name = :destination_type)
        )
        RETURNING id
        """
        )

        return self.connection.execute(
            func_key_query,
            func_key_type=func_key_type,
            destination_type=destination_type,
        ).scalar()

    def insert_destination(self, table, column, func_key_id, destination_id):
        destination_query = text(
            """
        INSERT INTO func_key_dest_{table} (func_key_id, {column})
        VALUES (:func_key_id, :destination_id)
        """.format(
                table=table, column=column
            )
        )

        self.connection.execute(
            destination_query, func_key_id=func_key_id, destination_id=destination_id
        )

    def insert_conference_only(self, name='myconf', number='2000', context='default'):
        conf_query = text(
            """
        INSERT INTO meetmefeatures

        (meetmeid,
        name,
        confno,
        context,
        admin_identification,
        admin_mode,
        admin_announcejoinleave,
        user_mode,
        user_announcejoinleave,
        emailbody,
        description)

        VALUES

        (:meetmeid,
        :name,
        :confno,
        :context,
        :admin_identification,
        :admin_mode,
        :admin_announcejoinleave,
        :user_mode,
        :user_announcejoinleave,
        :emailbody,
        :description)

        RETURNING id
        """
        )

        conference_id = self.connection.execute(
            conf_query,
            meetmeid=1234,
            name=name,
            confno=number,
            context=context,
            admin_identification='pin',
            admin_mode='all',
            admin_announcejoinleave='no',
            user_mode='all',
            user_announcejoinleave='no',
            emailbody='email',
            description='',
        ).scalar()

        return conference_id

    def insert_conference(self, name='myconf', number='2000', context='default'):
        conference_id = self.insert_conference_only(
            name=name, number=number, context=context
        )

        self.insert_extension(number, context, 'meetme', conference_id)

        func_key_id = self.insert_func_key('speeddial', 'conference')
        self.insert_destination(
            'conference', 'conference_id', func_key_id, conference_id
        )

        return conference_id

    def delete_conference(self, meetme_id):
        query = text("DELETE FROM meetmefeatures WHERE id = :meetme_id")
        self.connection.execute(query, meetme_id=meetme_id)

    def get_conferences(self):
        query = text("SELECT * FROM meetmefeatures")
        return self.connection.execute(query)

    def insert_extension(self, exten, context, type_, typeval):
        exten_query = text(
            """
        INSERT INTO extensions (context, exten, type, typeval)
        VALUES (:context, :exten, :type, :typeval)
        RETURNING id
        """
        )

        return self.connection.execute(
            exten_query, context=context, exten=exten, type=type_, typeval=str(typeval)
        ).scalar()

    def insert_group(
        self, name='mygroup', number='1234', context='default', tenant_uuid=None
    ):
        query = text(
            """
        INSERT INTO groupfeatures (name, tenant_uuid)
        VALUES (:name, :tenant_uuid)
        RETURNING id
        """
        )

        group_id = self.connection.execute(
            query, name=name, tenant_uuid=tenant_uuid
        ).scalar()
        self.insert_extension(number, context, 'group', group_id)

        func_key_id = self.insert_func_key('speeddial', 'group')
        self.insert_destination('group', 'group_id', func_key_id, group_id)

        return group_id

    def insert_agent(
        self, number='1000', context='default', group_name='default', tenant_uuid=None
    ):
        query = text(
            """
        INSERT INTO agentfeatures
        (numgroup, number, passwd, context, language, description, tenant_uuid)
        VALUES (
            (SELECT groupid FROM agentgroup WHERE name = :group_name),
            :number,
            '',
            :context,
            '',
            '',
            :tenant_uuid
        )
        RETURNING id
        """
        )

        func_key_query = text(
            """
        INSERT INTO func_key_dest_agent (func_key_id, agent_id, extension_id)
        VALUES (
        :func_key_id,
        :agent_id,
        (SELECT id FROM extensions WHERE type = 'extenfeatures' AND typeval = :typeval)
        )
        """
        )

        agent_id = self.connection.execute(
            query,
            number=number,
            context=context,
            group_name=group_name,
            tenant_uuid=tenant_uuid,
        ).scalar()

        func_key_id = self.insert_func_key('speeddial', 'agent')

        for typeval in (
            'agentstaticlogin',
            'agentstaticlogoff',
            'agentstaticlogtoggle',
        ):
            func_key_id = self.insert_func_key('speeddial', 'agent')
            self.connection.execute(
                func_key_query,
                func_key_id=func_key_id,
                agent_id=agent_id,
                typeval=typeval,
            )

        return agent_id

    def get_agent(self):
        query = text("SELECT * FROM agentfeatures")
        return self.connection.execute(query)

    def insert_agent_login_status(self, context='default'):
        query = text(
            """
        INSERT INTO agent_login_status (agent_id, agent_number, extension, context, interface, state_interface)
        VALUES (1, '1234', '1234', :context, 'interface', 'state')
        RETURNING agent_id
        """
        )

        agent_id = self.connection.execute(query, context=context).scalar()

        return agent_id

    def delete_agent_login_status(self, agent_id):
        query = text("DELETE FROM agent_login_status WHERE agent_id = :agent_id")
        self.connection.execute(query, agent_id=agent_id)

    def insert_paging(self, number='1234', tenant_uuid=None):
        query = text(
            """
        INSERT INTO paging (number, timeout, tenant_uuid)
        VALUES (:number, :timeout, :tenant_uuid)
        RETURNING id
        """
        )

        paging_id = self.connection.execute(
            query, number=number, timeout=30, tenant_uuid=tenant_uuid
        ).scalar()

        func_key_id = self.insert_func_key('speeddial', 'paging')
        self.insert_destination('paging', 'paging_id', func_key_id, paging_id)

        return paging_id

    def insert_callfilter(
        self,
        name='bsfilter',
        type_='bosssecretary',
        bosssecretary='secretary-simult',
        tenant_uuid=None,
    ):
        query = text(
            """
        INSERT INTO callfilter (name, type, bosssecretary, tenant_uuid)
        VALUES (
        :name,
        :type,
        :bosssecretary,
        :tenant_uuid
        )
        RETURNING id
        """
        )

        return self.connection.execute(
            query,
            name=name,
            type=type_,
            bosssecretary=bosssecretary,
            tenant_uuid=tenant_uuid,
        ).scalar()

    def insert_filter_member(self, callfilter_id, member_id, bstype='secretary'):
        query = text(
            """
        INSERT INTO callfiltermember (callfilterid, type, typeval, bstype)
        VALUES (:callfilterid, :type, :typeval, :bstype)
        RETURNING id
        """
        )

        filter_member_id = self.connection.execute(
            query,
            callfilterid=callfilter_id,
            type='user',
            typeval=str(member_id),
            bstype=bstype,
        ).scalar()

        func_key_id = self.insert_func_key('speeddial', 'bsfilter')
        self.insert_destination(
            'bsfilter', 'filtermember_id', func_key_id, filter_member_id
        )

        return filter_member_id

    def delete_context(self, name):
        query = text("DELETE FROM context WHERE name = :name")
        self.connection.execute(query, name=name)

    def associate_line_device(self, line_id, device_id):
        query = text("UPDATE linefeatures SET device = :device_id WHERE id = :line_id")
        self.connection.execute(query, device_id=device_id, line_id=line_id)

    def dissociate_line_device(self, line_id, device_id):
        query = text("UPDATE linefeatures SET device = NULL WHERE id = :line_id")
        self.connection.execute(query, device_id=device_id, line_id=line_id)

    def line_has_sccp_device(self, line_id, sccp_device):
        query = text(
            """SELECT COUNT(*)
                     FROM linefeatures
                        INNER JOIN sccpline
                            ON linefeatures.protocol = 'sccp'
                            AND linefeatures.protocolid = sccpline.id
                            INNER JOIN sccpdevice ON sccpdevice.line = linefeatures.name
                     WHERE
                        linefeatures.id = :line_id
                        AND sccpdevice.device = :sccp_device
                     """
        )

        count = self.connection.execute(
            query, line_id=line_id, sccp_device=sccp_device
        ).scalar()

        return count > 0

    def sccp_device_exists(self, sccp_device):
        query = text(
            """SELECT COUNT(*)
                     FROM sccpdevice
                     WHERE
                        sccpdevice.device = :sccp_device
                     """
        )
        count = self.connection.execute(query, sccp_device=sccp_device).scalar()
        return count > 0

    def sip_has_language(self, language):
        query = text(
            """SELECT COUNT(*)
                     FROM staticsip
                     WHERE
                        var_name = 'language'
                        AND var_val = :language
                     """
        )
        count = self.connection.execute(query, language=language).scalar()

        return count > 0

    def iax_has_language(self, language):
        query = text(
            """SELECT COUNT(*)
                     FROM staticiax
                     WHERE
                        var_name = 'language'
                        AND var_val = :language
                     """
        )
        count = self.connection.execute(query, language=language).scalar()

        return count > 0

    def sccp_has_language(self, language):
        query = text(
            """SELECT COUNT(*)
                     FROM sccpgeneralsettings
                     WHERE
                        option_name = 'language'
                        AND option_value = :language
                     """
        )
        count = self.connection.execute(query, language=language).scalar()

        return count > 0

    def general_has_timezone(self, timezone):
        query = text(
            """SELECT COUNT(*)
                     FROM general
                     WHERE
                        timezone = :timezone
                     """
        )
        count = self.connection.execute(query, timezone=timezone).scalar()

        return count > 0

    def resolvconf_is_configured(self, hostname, domain, nameservers):
        query = text(
            """SELECT COUNT(*)
                     FROM resolvconf
                     WHERE
                        hostname = :hostname
                        AND domain = :domain
                        AND search = :domain
                        AND nameserver1 = :nameserver1
                        AND nameserver2 = :nameserver2
                     """
        )

        count = self.connection.execute(
            query,
            hostname=hostname,
            domain=domain,
            nameserver1=nameservers[0],
            nameserver2=nameservers[1],
        ).scalar()

        return count > 0

    def netiface_is_configured(self, address, gateway):
        # Note that interface and netmask are not tested
        query = text(
            """SELECT COUNT(*)
                     FROM netiface
                     WHERE
                        hwtypeid = 1
                        AND type = 'iface'
                        AND family = 'inet'
                        AND method = 'static'
                        AND address = :address
                        AND broadcast = ''
                        AND gateway = :gateway
                        AND mtu = 1500
                        AND options = ''
                     """
        )

        count = self.connection.execute(
            query, address=address, gateway=gateway
        ).scalar()

        return count > 0

    def context_has_internal(self, display_name, number_start, number_end):
        query = text(
            """SELECT COUNT(*)
                     FROM context
                     INNER JOIN contextnumbers
                        ON context.name = contextnumbers.context
                     WHERE
                        context.name = 'default'
                        AND context.displayname = :display_name
                        AND context.contexttype = 'internal'
                        AND contextnumbers.type = 'user'
                        AND contextnumbers.numberbeg = :number_start
                        AND contextnumbers.numberend = :number_end
                        AND contextnumbers.didlength = 0
                     """
        )

        count = self.connection.execute(
            query,
            display_name=display_name,
            number_start=number_start,
            number_end=number_end,
        ).scalar()

        return count > 0


def create_helper(
    user='asterisk',
    password='proformatique',
    host='localhost',
    port=5432,
    db='asterisk',
):
    return DbHelper.build(user, password, host, port, db)
