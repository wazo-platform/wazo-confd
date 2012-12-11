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

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import mapper
from sqlalchemy.orm.exc import UnmappedClassError
from sqlalchemy.orm.util import class_mapper
from sqlalchemy.schema import Table, MetaData
from xivo_dao.alchemy import dbconnection
from xivo_recording.dao.generic_dao import GenericDao
from xivo_recording.dao.helpers.dynamic_formatting import \
    table_list_to_list_dict
from xivo_recording.recording_config import RecordingConfig
import logging

logger = logging.getLogger(__name__)
logging.basicConfig()

class RecordCampaignDao(GenericDao):
    pass


class RecordCampaignDbBinder(object):

    __tablename__ = "record_campaign"

    def __init__(self, session):
        self.session = session

    def get_records_as_dict(self):
        return table_list_to_list_dict(self.session.query(RecordCampaignDao).all())

    def get_records(self):
        return self.session.query(RecordCampaignDao).all()

    def add(self, params):
        record = RecordCampaignDao()
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
    def create_class_mapper(cls, uri):
            engine = create_engine(uri, echo=RecordingConfig.POSTGRES_DEBUG)
            metadata = MetaData(engine)
            data = Table(cls.__tablename__, metadata, autoload=True)
            mapper(RecordCampaignDao, data)

    @classmethod
    def new_from_uri(cls, uri):
        try:
            class_mapper(RecordCampaignDao)
        except UnmappedClassError:
            try:
                cls.create_class_mapper(uri)
            except BaseException as e:
                logger.error("Database access error: " + str(e.args))
                return None
        except BaseException as e:
            logger.error("Database access error:" + str(e.args))
            return None

        connection = dbconnection.get_connection(uri)
        return cls(connection.get_session())

