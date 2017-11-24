# -*- coding: UTF-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import sqlalchemy as sa

from contextlib import contextmanager
from sqlalchemy.sql import text


class DbHelper(object):

    TEMPLATE = "xivotemplate"

    @classmethod
    def build(cls, user, password, host, port, db):
        tpl = "postgresql://{user}:{password}@{host}:{port}"
        uri = tpl.format(user=user,
                         password=password,
                         host=host,
                         port=port)
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
        connection.execute("""
                           SELECT pg_terminate_backend(pg_stat_activity.pid)
                           FROM pg_stat_activity
                           WHERE pg_stat_activity.datname = '{db}'
                           AND pid <> pg_backend_pid()
                           """.format(db=self.db))
        connection.execute("DROP DATABASE IF EXISTS {db}".format(db=self.db))
        connection.execute("CREATE DATABASE {db} TEMPLATE {template}".format(db=self.db,
                                                                             template=self.TEMPLATE))
        connection.close()

    def execute(self, query, **kwargs):
        with self.connect() as connection:
            connection.execute(text(query), **kwargs)

    @contextmanager
    def queries(self):
        with self.connect() as connection:
            yield DatabaseQueries(connection)


class DatabaseQueries(object):

    def __init__(self, connection):
        self.connection = connection

    def insert_queue(self, name='myqueue', number='3000', context='default'):
        queue_query = text("""
        INSERT INTO queuefeatures (name, displayname, number, context)
        VALUES (:name, :displayname, :number, :context)
        RETURNING id
        """)

        queue_id = (self.connection
                    .execute(queue_query,
                             name=name,
                             displayname=name,
                             number=number,
                             context=context)
                    .scalar())

        self.insert_extension(number, context, 'queue', queue_id)

        func_key_id = self.insert_func_key('speeddial', 'queue')
        self.insert_destination('queue', 'queue_id', func_key_id, queue_id)

        return queue_id

    def insert_queue_only(self, name, displayname='', number='', context=None):
        queuefeatures_query = text("""
        INSERT INTO queuefeatures (name, displayname, number, context)
        VALUES (:name, :displayname, :number, :context)
        RETURNING id
        """)

        queuefeatures_id = (self.connection
                            .execute(queuefeatures_query,
                                     name=name,
                                     displayname=name,
                                     number=number,
                                     context=context)
                            .scalar())

        queue_query = text("""
        INSERT INTO queue (name, category)
        VALUES (:name, 'queue')
        RETURNING name
        """)
        self.connection.execute(queue_query, name=name).scalar()

        return queuefeatures_id

    def delete_queue(self, queue_id):
        query = text("DELETE FROM queue WHERE name = (SELECT name FROM queuefeatures WHERE id = :queue_id)")
        self.connection.execute(query, queue_id=queue_id)
        query = text("DELETE FROM queuefeatures WHERE id = :queue_id")
        self.connection.execute(query, queue_id=queue_id)

    def get_queues(self):
        query = text("SELECT * FROM queuefeatures")
        return self.connection.execute(query)

    def associate_queue_extension(self, queue_id, extension_id):
        query = text("UPDATE extensions SET type = 'queue', typeval = :queue_id WHERE id = :extension_id")
        self.connection.execute(query, queue_id=queue_id, extension_id=extension_id)

    def dissociate_queue_extension(self, queue_id, extension_id):
        query = text("UPDATE extensions SET type = 'user', typeval = 0 WHERE id = :extension_id")
        self.connection.execute(query, extension_id=extension_id)

    def insert_func_key(self, func_key_type, destination_type):
        func_key_query = text("""
        INSERT INTO func_key (type_id, destination_type_id)
        VALUES (
        (SELECT id FROM func_key_type WHERE name = :func_key_type),
        (SELECT id FROM func_key_destination_type WHERE name = :destination_type)
        )
        RETURNING id
        """)

        return (self.connection
                .execute(func_key_query,
                         func_key_type=func_key_type,
                         destination_type=destination_type)
                .scalar())

    def insert_destination(self, table, column, func_key_id, destination_id):
        destination_query = text("""
        INSERT INTO func_key_dest_{table} (func_key_id, {column})
        VALUES (:func_key_id, :destination_id)
        """.format(table=table, column=column))

        self.connection.execute(destination_query,
                                func_key_id=func_key_id,
                                destination_id=destination_id)

    def insert_conference_only(self, name='myconf', number='2000', context='default'):
        conf_query = text("""
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
        """)

        conference_id = (self.connection
                         .execute(conf_query,
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
                                  description='')
                         .scalar())

        return conference_id

    def insert_conference(self, name='myconf', number='2000', context='default'):
        conference_id = self.insert_conference_only(name=name, number=number, context=context)

        self.insert_extension(number, context, 'meetme', conference_id)

        func_key_id = self.insert_func_key('speeddial', 'conference')
        self.insert_destination('conference', 'conference_id', func_key_id, conference_id)

        return conference_id

    def delete_conference(self, meetme_id):
        query = text("DELETE FROM meetmefeatures WHERE id = :meetme_id")
        self.connection.execute(query, meetme_id=meetme_id)

    def get_conferences(self):
        query = text("SELECT * FROM meetmefeatures")
        return self.connection.execute(query)

    def insert_extension(self, exten, context, type_, typeval):
        exten_query = text("""
        INSERT INTO extensions (context, exten, type, typeval)
        VALUES (:context, :exten, :type, :typeval)
        RETURNING id
        """)

        return (self.connection
                .execute(exten_query,
                         context=context,
                         exten=exten,
                         type=type_,
                         typeval=str(typeval))
                .scalar())

    def insert_group(self, name='mygroup', number='1234', context='default'):
        query = text("""
        INSERT INTO groupfeatures (name, number, context)
        VALUES (:name, :number, :context)
        RETURNING id
        """)

        group_id = (self.connection
                    .execute(query,
                             name=name,
                             number=number,
                             context=context)
                    .scalar())
        self.insert_extension(number, context, 'group', group_id)

        func_key_id = self.insert_func_key('speeddial', 'group')
        self.insert_destination('group', 'group_id', func_key_id, group_id)

        return group_id

    def insert_agent(self, number='1000', context='default', group_name='default'):
        query = text("""
        INSERT INTO agentfeatures
        (numgroup, number, passwd, context, language, description)
        VALUES (
            (SELECT groupid FROM agentgroup WHERE name = :group_name),
            :number,
            '',
            :context,
            '',
            ''
        )
        RETURNING id
        """)

        func_key_query = text("""
        INSERT INTO func_key_dest_agent (func_key_id, agent_id, extension_id)
        VALUES (
        :func_key_id,
        :agent_id,
        (SELECT id FROM extensions WHERE type = 'extenfeatures' AND typeval = :typeval)
        )
        """)

        agent_id = (self.connection
                    .execute(query,
                             number=number,
                             context=context,
                             group_name=group_name)
                    .scalar())

        func_key_id = self.insert_func_key('speeddial', 'agent')

        for typeval in ('agentstaticlogin', 'agentstaticlogoff', 'agentstaticlogtoggle'):
            func_key_id = self.insert_func_key('speeddial', 'agent')
            self.connection.execute(func_key_query,
                                    func_key_id=func_key_id,
                                    agent_id=agent_id,
                                    typeval=typeval)

        return agent_id

    def get_agent(self):
        query = text("SELECT * FROM agentfeatures")
        return self.connection.execute(query)

    def delete_agent(self, agent_id):
        query = text("DELETE FROM func_key_dest_agent WHERE agent_id = :agent_id")
        self.connection.execute(query, agent_id=agent_id)

        query = text("DELETE FROM agentfeatures WHERE id = :agent_id")
        self.connection.execute(query, agent_id=agent_id)

    def insert_agent_login_status(self, context='default'):
        query = text("""
        INSERT INTO agent_login_status (agent_id, agent_number, extension, context, interface, state_interface)
        VALUES (1, '1234', '1234', :context, 'interface', 'state')
        RETURNING agent_id
        """)

        agent_id = (self.connection
                    .execute(query,
                             context=context)
                    .scalar())

        return agent_id

    def delete_agent_login_status(self, agent_id):
        query = text("DELETE FROM agent_login_status WHERE agent_id = :agent_id")
        self.connection.execute(query, agent_id=agent_id)

    def insert_paging(self, number='1234'):
        query = text("""
        INSERT INTO paging (number, timeout)
        VALUES (:number, :timeout)
        RETURNING id
        """)

        paging_id = (self.connection
                     .execute(query,
                              number=number,
                              timeout=30)
                     .scalar())

        func_key_id = self.insert_func_key('speeddial', 'paging')
        self.insert_destination('paging', 'paging_id', func_key_id, paging_id)

        return paging_id

    def insert_callfilter(self, name='bsfilter', type_='bosssecretary', bosssecretary='secretary-simult'):
        query = text("""
        INSERT INTO callfilter (entity_id, name, type, bosssecretary, description)
        VALUES (
        (SELECT id FROM entity LIMIT 1),
        :name,
        :type,
        :bosssecretary,
        '')
        RETURNING id
        """)

        return (self.connection
                .execute(query,
                         name=name,
                         type=type_,
                         bosssecretary=bosssecretary)
                .scalar())

    def insert_filter_member(self, callfilter_id, member_id, bstype='secretary'):
        query = text("""
        INSERT INTO callfiltermember (callfilterid, type, typeval, bstype)
        VALUES (:callfilterid, :type, :typeval, :bstype)
        RETURNING id
        """)

        filter_member_id = (self.connection
                            .execute(query,
                                     callfilterid=callfilter_id,
                                     type='user',
                                     typeval=str(member_id),
                                     bstype=bstype)
                            .scalar())

        func_key_id = self.insert_func_key('speeddial', 'bsfilter')
        self.insert_destination('bsfilter', 'filtermember_id', func_key_id, filter_member_id)

        return filter_member_id

    def associate_context_entity(self, context_name, entity_name):
        query = text("UPDATE context SET entity = :entity_name WHERE name = :context_name")
        self.connection.execute(query, entity_name=entity_name, context_name=context_name)

    def delete_context(self, name):
        query = text("DELETE FROM context WHERE name = :name")
        self.connection.execute(query, name=name)

    def insert_cti_profile(self, name):
        query = text("""
                     INSERT INTO cti_profile(name) VALUES (:name) RETURNING id
                     """)

        cti_profile_id = self.connection.execute(query, name=name).scalar()
        return cti_profile_id

    def delete_cti_profile(self, cti_profile_id):
        query = text("DELETE FROM cti_profile WHERE id = :cti_profile_id")
        self.connection.execute(query, cti_profile_id=cti_profile_id)

    def dissociate_cti_profile(self, cti_profile_id):
        query = text("UPDATE userfeatures SET cti_profile_id = NULL WHERE cti_profile_id = :cti_profile_id")
        self.connection.execute(query, cti_profile_id=cti_profile_id)

    def insert_call_pickup(self, name):
        query = text("""
        INSERT INTO pickup (id, name, description, entity_id)
        VALUES (
                     1, :name, '',
                     (SELECT id FROM entity LIMIT 1)
               )
        RETURNING id
        """)

        call_pickup_id = (self.connection
                          .execute(query,
                                   name=name)
                          .scalar())

        return call_pickup_id

    def delete_call_pickup(self, call_pickup_id):
        query = text("DELETE FROM pickup WHERE id = :id")
        self.connection.execute(query, id=call_pickup_id)

    def associate_call_pickup_entity(self, call_pickup_id, entity_id):
        query = text("UPDATE pickup SET entity_id = :entity_id WHERE id = :call_pickup_id")
        self.connection.execute(query, entity_id=entity_id, call_pickup_id=call_pickup_id)

    def insert_call_filter(self, name):
        query = text("""
        INSERT INTO callfilter (name, type, description)
        VALUES (
                     :name, 'bosssecretary', ''
               )
        RETURNING id
        """)

        call_filter_id = (self.connection
                          .execute(query,
                                   name=name)
                          .scalar())

        return call_filter_id

    def delete_call_filter(self, call_filter_id):
        query = text("DELETE FROM callfilter WHERE id = :id")
        self.connection.execute(query, id=call_filter_id)

    def associate_call_filter_entity(self, call_filter_id, entity_id):
        query = text("UPDATE callfilter SET entity_id = :entity_id WHERE id = :call_filter_id")
        self.connection.execute(query, entity_id=entity_id, call_filter_id=call_filter_id)

    def associate_schedule_entity(self, schedule_id, entity_id):
        query = text("UPDATE schedule SET entity_id = :entity_id WHERE id = :schedule_id")
        self.connection.execute(query, entity_id=entity_id, schedule_id=schedule_id)

    def associate_line_device(self, line_id, device_id):
        query = text("UPDATE linefeatures SET device = :device_id WHERE id = :line_id")
        self.connection.execute(query, device_id=device_id, line_id=line_id)

    def dissociate_line_device(self, line_id, device_id):
        query = text("UPDATE linefeatures SET device = NULL WHERE id = :line_id")
        self.connection.execute(query, device_id=device_id, line_id=line_id)

    def line_has_sccp_device(self, line_id, sccp_device):
        query = text("""SELECT COUNT(*)
                     FROM linefeatures
                        INNER JOIN sccpline
                            ON linefeatures.protocol = 'sccp'
                            AND linefeatures.protocolid = sccpline.id
                            INNER JOIN sccpdevice ON sccpdevice.line = linefeatures.name
                     WHERE
                        linefeatures.id = :line_id
                        AND sccpdevice.device = :sccp_device
                     """)

        count = (self.connection
                 .execute(query,
                          line_id=line_id,
                          sccp_device=sccp_device)
                 .scalar())

        return count > 0

    def admin_has_password(self, password):
        query = text("""SELECT COUNT(*)
                     FROM "user"
                     WHERE
                        login = 'root'
                        AND passwd = :password
                     """)
        count = (self.connection
                 .execute(query,
                          password=password)
                 .scalar())

        return count > 0

    def autoprov_is_configured(self):
        query = text("""SELECT COUNT(*)
                     FROM staticsip
                     WHERE
                        category = 'general'
                        AND filename = 'sip.conf'
                        AND var_name = 'autocreate_prefix'
                     """)
        count = (self.connection
                 .execute(query)
                 .scalar())

        return count > 0

    def entity_has_name_displayname(self, name, displayname):
        query = text("""SELECT COUNT(*)
                     FROM entity
                     WHERE
                        name = :name
                        AND displayname = :displayname
                     """)
        count = (self.connection
                 .execute(query,
                          name=name,
                          displayname=displayname)
                 .scalar())

        return count > 0

    def sip_has_language(self, language):
        query = text("""SELECT COUNT(*)
                     FROM staticsip
                     WHERE
                        var_name = 'language'
                        AND var_val = :language
                     """)
        count = (self.connection
                 .execute(query,
                          language=language)
                 .scalar())

        return count > 0

    def iax_has_language(self, language):
        query = text("""SELECT COUNT(*)
                     FROM staticiax
                     WHERE
                        var_name = 'language'
                        AND var_val = :language
                     """)
        count = (self.connection
                 .execute(query,
                          language=language)
                 .scalar())

        return count > 0

    def sccp_has_language(self, language):
        query = text("""SELECT COUNT(*)
                     FROM sccpgeneralsettings
                     WHERE
                        option_name = 'language'
                        AND option_value = :language
                     """)
        count = (self.connection
                 .execute(query,
                          language=language)
                 .scalar())

        return count > 0

    def general_has_timezone(self, timezone):
        query = text("""SELECT COUNT(*)
                     FROM general
                     WHERE
                        timezone = :timezone
                     """)
        count = (self.connection
                 .execute(query,
                          timezone=timezone)
                 .scalar())

        return count > 0

    def resolvconf_is_configured(self, hostname, domain, nameservers):
        query = text("""SELECT COUNT(*)
                     FROM resolvconf
                     WHERE
                        hostname = :hostname
                        AND domain = :domain
                        AND search = :domain
                        AND nameserver1 = :nameserver1
                        AND nameserver2 = :nameserver2
                     """)

        count = (self.connection
                 .execute(query,
                          hostname=hostname,
                          domain=domain,
                          nameserver1=nameservers[0],
                          nameserver2=nameservers[1])
                 .scalar())

        return count > 0

    def netiface_is_configured(self, address, gateway):
        # Note that interface and netmask are not tested
        query = text("""SELECT COUNT(*)
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
                     """)

        count = (self.connection
                 .execute(query,
                          address=address,
                          gateway=gateway)
                 .scalar())

        return count > 0

    def context_has_internal(self, display_name, number_start, number_end):
        query = text("""SELECT COUNT(*)
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
                     """)

        count = (self.connection
                 .execute(query,
                          display_name=display_name,
                          number_start=number_start,
                          number_end=number_end)
                 .scalar())

        return count > 0

    def context_has_incall(self, display_name=None, number_start=None, number_end=None, did_length=None):
        if number_start is None and number_end is None:
            query = text("""SELECT COUNT(*)
                         FROM context
                         WHERE
                            context.name = 'from-extern'
                            AND context.displayname = :display_name
                            AND context.contexttype = 'incall'
                         """)

            count = (self.connection
                     .execute(query,
                              display_name=display_name)
                     .scalar())
        else:
            query = text("""SELECT COUNT(*)
                         FROM context
                         INNER JOIN contextnumbers
                            ON context.name = contextnumbers.context
                         WHERE
                            context.name = 'from-extern'
                            AND context.displayname = :display_name
                            AND context.contexttype = 'incall'
                            AND contextnumbers.type = 'incall'
                            AND contextnumbers.numberbeg = :number_start
                            AND contextnumbers.numberend = :number_end
                            AND contextnumbers.didlength = :did_length
                         """)

            count = (self.connection
                     .execute(query,
                              display_name=display_name,
                              number_start=number_start,
                              number_end=number_end,
                              did_length=did_length)
                     .scalar())

        return count > 0

    def context_has_outcall(self, display_name):
        query = text("""SELECT COUNT(*)
                     FROM context
                     WHERE
                        context.name = 'to-extern'
                        AND context.displayname = :display_name
                        AND context.contexttype = 'outcall'
                     """)

        count = (self.connection
                 .execute(query,
                          display_name=display_name)
                 .scalar())

        return count > 0

    def context_has_switchboard(self):
        query = text("""SELECT COUNT(*)
                     FROM context
                     WHERE
                        context.name = '__switchboard_directory'
                        AND context.displayname = 'Switchboard'
                        AND context.contexttype = 'others'
                     """)

        count = (self.connection
                 .execute(query)
                 .scalar())

        return count > 0

    def internal_context_include_outcall_context(self):
        query = text("""SELECT COUNT(*)
                     FROM contextinclude
                     WHERE
                        context = 'default'
                        AND include = 'to-extern'
                        AND priority = 0
                     """)

        count = (self.connection
                 .execute(query)
                 .scalar())

        return count > 0

    def insert_call_log(self, date, date_answer, date_end, source_name, source_exten, destination_exten, user_field):
        query = text("""INSERT INTO call_log(date, date_answer, date_end, source_name, source_exten, destination_exten, user_field)
                        VALUES (:date, :date_answer, :date_end, :source_name, :source_exten, :destination_exten, :user_field)
                        RETURNING id""")
        return self.connection.execute(query,
                                       date=date,
                                       date_answer=date_answer,
                                       date_end=date_end,
                                       source_name=source_name,
                                       source_exten=source_exten,
                                       destination_exten=destination_exten,
                                       user_field=user_field).scalar()

    def delete_call_log(self, call_log_id):
        query = text("""DELETE from call_log
                        WHERE id = :id""")
        self.connection.execute(query, id=call_log_id)

    def profile_as_phonebook_for_lookup(self):
        query = text("""select count(id) from cticontexts where directories like '%wazophonebook%'""")
        return self.connection.execute(query).scalar() == 2  # default and __switchboard

    def profile_as_phonebook_for_reverse_lookup(self):
        query = text("""select count(id) from ctireversedirectories where directories like '%wazophonebook%'""")
        return self.connection.execute(query).scalar() == 1

    def phonebook_source_is_configured(self):
        query = text("""select count(*) from ctidirectories, directories where ctidirectories.directory_id = directories.id and directories.dirtype='dird_phonebook'""")
        ctidirectories_configured = self.connection.execute(query).scalar() == 1
        query = text("""select count(ctidirectoryfields) from ctidirectoryfields, ctidirectories, directories where ctidirectoryfields.dir_id = ctidirectories.id and ctidirectories.directory_id = directories.id and directories.dirtype='dird_phonebook'""")
        fields_configured = self.connection.execute(query).scalar() == 9
        return ctidirectories_configured and fields_configured


def create_helper(user='asterisk', password='proformatique', host='localhost', port=5432, db='asterisk'):
    return DbHelper.build(user, password, host, port, db)
