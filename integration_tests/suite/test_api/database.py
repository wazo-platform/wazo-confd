import os
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
                           SELECT pg_terminate_backend(pg_stat_activity.procpid)
                           FROM pg_stat_activity
                           WHERE pg_stat_activity.datname = '{db}'
                           AND procpid <> pg_backend_pid()
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

    def insert_conference(self, name='myconf', number='2000', context='default'):
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

        self.insert_extension(number, context, 'meetme', conference_id)

        func_key_id = self.insert_func_key('speeddial', 'conference')
        self.insert_destination('conference', 'conference_id', func_key_id, conference_id)

        return conference_id

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

    def insert_agent(self, number='1000', context='default'):
        query = text("""
        INSERT INTO agentfeatures
        (numgroup, number, passwd, context, language, description)
        VALUES (
            (SELECT groupid FROM agentgroup WHERE name = :context),
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
                             context=context)
                    .scalar())

        func_key_id = self.insert_func_key('speeddial', 'agent')

        for typeval in ('agentstaticlogin', 'agentstaticlogoff', 'agentstaticlogtoggle'):
            func_key_id = self.insert_func_key('speeddial', 'agent')
            self.connection.execute(func_key_query,
                                    func_key_id=func_key_id,
                                    agent_id=agent_id,
                                    typeval=typeval)

        return agent_id

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

    def associate_line_device(self, line_id, device_id):
        query = text("UPDATE linefeatures SET device = :device_id WHERE id = :line_id")
        self.connection.execute(query, device_id=device_id, line_id=line_id)

    def dissociate_line_device(self, line_id, device_id):
        query = text("UPDATE linefeatures SET device = NULL WHERE id = :line_id")
        self.connection.execute(query, device_id=device_id, line_id=line_id)


def create_helper():
    user = os.environ.get('DB_USER', 'asterisk')
    password = os.environ.get('DB_PASSORD', 'proformatique')
    host = os.environ.get('DB_HOST', 'localhost')
    port = os.environ.get('DB_PORT', 15432)
    db = os.environ.get('DB_NAME', 'asterisk')

    return DbHelper.build(user, password, host, port, db)
