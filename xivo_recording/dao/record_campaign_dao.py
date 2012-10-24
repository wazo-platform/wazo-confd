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


class RecordCampaignDao(GenericDao):
    pass


class RecordCampaignDbBinder(object):

    __tablename__ = "record_campaign"

    def __init__(self, session):
        self.session = session

    def get_records(self):
        return self.session.query(RecordCampaignDao).all()

    def insert_into(self, params):
        record = RecordCampaignDao()
        for k, v in params.items():
            setattr(record, k, v)
        self.session.add(record)
        self.session.commit()

    @classmethod
    def new_from_uri(cls, uri):
        engine = create_engine(uri, echo=RecordingConfig.POSTGRES_DEBUG)
        metadata = MetaData(engine)
        data = Table(cls.__tablename__, metadata, autoload=True)
        mapper(RecordCampaignDao, data)

        connection = dbconnection.get_connection(uri)
        return cls(connection.get_session())
