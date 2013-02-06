# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# XiVO CTI Server
# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, TEXT
from xivo_dao.alchemy.base import Base


class AccessWebService(Base):

    __tablename__ = 'accesswebservice'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    login = Column(String(64))
    passwd = Column(String(64))
    host = Column(String(255))
    obj = Column(TEXT, nullable=False)
    disable = Column(Integer, nullable=False, default=0)
    description = Column(TEXT, nullable=False)
