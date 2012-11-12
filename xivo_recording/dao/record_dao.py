# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from sqlalchemy.schema import Table, MetaData
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import mapper
from xivo_dao.alchemy import dbconnection
from recording_config import RecordingConfig
from dao.generic_dao import GenericDao
from sqlalchemy.orm.util import class_mapper
from sqlalchemy.orm.exc import UnmappedClassError
from dao.helpers.dynamic_formatting import table_list_to_list_dict


class RecordDao(GenericDao):
    pass


class RecordDbBinder(object):

    __tablename__ = "recording"

    def __init__(self, session):
        self.session = session

    def get_records_as_list(self):
        return table_list_to_list_dict(self.session.query(RecordDao).all())

    def get_records(self):
        return self.session.query(RecordDao).all()

    def add(self, params):
        record = RecordDao()
        for k, v in params.items():
            setattr(record, k, v)
        try:
            self.session.add(record)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return True

    @classmethod
    def new_from_uri(cls, uri):
        try:
            class_mapper(RecordDao)
        except UnmappedClassError:
            engine = create_engine(uri, echo=RecordingConfig.POSTGRES_DEBUG)
            metadata = MetaData(engine)
            data = Table(cls.__tablename__, metadata, autoload=True)
            mapper(RecordDao, data)

        connection = dbconnection.get_connection(uri)
        return cls(connection.get_session())
