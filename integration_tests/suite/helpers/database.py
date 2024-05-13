# Copyright 2015-2024 The Wazo Authors  (see the AUTHORS file)
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
        uri = f"postgresql://{user}:{password}@{host}:{port}"
        return cls(uri, db)

    def __init__(self, uri, db):
        self.uri = uri
        self.db = db
        self._engine = self.create_engine()

    def create_engine(self, db=None, isolate=False):
        db = db or self.db
        uri = "{}/{}".format(self.uri, db)
        if isolate:
            return sa.create_engine(uri, isolation_level='AUTOCOMMIT')
        return sa.create_engine(uri)

    def connect(self):
        return self._engine.connect()

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
        self._engine = self.create_engine()

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

    def toggle_sip_templates_generated(self, tenant_uuid, generated=False):
        query = text(
            "UPDATE tenant SET sip_templates_generated = :generated WHERE uuid = :tenant_uuid"
        )
        self.connection.execute(
            query,
            generated='true' if generated else 'false',
            tenant_uuid=tenant_uuid,
        )

    def set_tenant_templates(self, tenant_uuid, **template_uuids):
        for field, template_uuid in template_uuids.items():
            query = text(
                "UPDATE tenant SET {} = :template_uuid WHERE uuid = :tenant_uuid".format(
                    field
                )
            )
            self.connection.execute(
                query,
                template_uuid=template_uuid,
                tenant_uuid=tenant_uuid,
            )

    @contextmanager
    def tenant_guest_sip_template_temporarily_disabled(self, tenant_uuid):
        query = text(
            "SELECT meeting_guest_sip_template_uuid FROM tenant WHERE uuid = :tenant_uuid"
        )
        guest_sip_template_uuid = self.connection.execute(
            query, tenant_uuid=tenant_uuid
        ).scalar()
        query = text(
            'UPDATE tenant SET meeting_guest_sip_template_uuid = :template_uuid WHERE uuid = :tenant_uuid'
        )
        self.connection.execute(
            query,
            template_uuid=None,
            tenant_uuid=tenant_uuid,
        )

        try:
            yield
        finally:
            query = text(
                'UPDATE tenant SET meeting_guest_sip_template_uuid = :template_uuid WHERE uuid = :tenant_uuid'
            )
            self.connection.execute(
                query,
                template_uuid=guest_sip_template_uuid,
                tenant_uuid=tenant_uuid,
            )

    def insert_extension_feature(self, exten='1000', feature='default', enabled=True):
        query = text(
            """
        INSERT INTO feature_extension
        (exten, feature, enabled)
        VALUES (
            :exten,
            :feature,
            :enabled
        )
        RETURNING uuid
        """
        )

        feature_extension_uuid = self.connection.execute(
            query, exten=exten, feature=feature, enabled=enabled
        ).scalar()

        return feature_extension_uuid

    def delete_extension_feature(self, extension_feature_uuid):
        query = text(
            "DELETE FROM feature_extension WHERE uuid = :extension_feature_uuid"
        )
        self.connection.execute(query, extension_feature_uuid=extension_feature_uuid)

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

    def associate_line_device(self, line_id, device_id):
        query = text("UPDATE linefeatures SET device = :device_id WHERE id = :line_id")
        self.connection.execute(query, device_id=device_id, line_id=line_id)

    def line_has_sccp_device(self, line_id, sccp_device):
        query = text(
            """SELECT COUNT(*)
                     FROM linefeatures
                        INNER JOIN sccpline
                            ON linefeatures.endpoint_sccp_id = sccpline.id
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

    def infos_has_timezone(self, timezone):
        query = text(
            """SELECT COUNT(*)
                     FROM infos
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

    def set_meeting_creation_date(self, meeting_uuid, date):
        query = text("UPDATE meeting SET created_at = :date WHERE uuid = :meeting_uuid")
        self.connection.execute(query, date=date, meeting_uuid=meeting_uuid)

    def set_meeting_authorization_creation_date(self, meeting_authorization_uuid, date):
        query = text(
            "UPDATE meeting_authorization SET created_at = :date WHERE uuid = :meeting_authorization_uuid"
        )
        self.connection.execute(
            query, date=date, meeting_authorization_uuid=meeting_authorization_uuid
        )

    @contextmanager
    def insert_max_meeting_authorizations(self, guest_uuid, meeting_uuid):
        query = text(
            """
        INSERT INTO meeting_authorization (meeting_uuid, guest_uuid, guest_name)
        VALUES (
            :meeting_uuid,
            :guest_uuid,
            :guest_name
        )
        """
        )

        for _ in range(128):
            self.connection.execute(
                query,
                meeting_uuid=meeting_uuid,
                guest_uuid=guest_uuid,
                guest_name='Dummy guest name',
            )

        yield

        query = text(
            "DELETE FROM meeting_authorization WHERE meeting_uuid = :meeting_uuid"
        )
        self.connection.execute(query, meeting_uuid=meeting_uuid)


def create_helper(
    user='asterisk',
    password='proformatique',
    host='127.0.0.1',
    port=5432,
    db='asterisk',
):
    return DbHelper.build(user, password, host, port, db)
