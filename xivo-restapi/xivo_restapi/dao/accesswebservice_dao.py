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
from functools import wraps
from sqlalchemy.engine import create_engine
from sqlalchemy.exc import OperationalError, InvalidRequestError
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.expression import and_, distinct
from xivo_restapi.dao.accesswebservice import AccessWebService
import logging


logger = logging.getLogger(__name__)
dbsession = None
_XIVO_DB_URI = 'postgresql://xivo:proformatique@localhost/xivo'


def xivo_connect():
    logger.debug('Connecting to database: %s' % _XIVO_DB_URI)
    engine = create_engine(_XIVO_DB_URI)
    Session = sessionmaker(bind=engine)
    return Session()


def xivo_reconnect():
    global dbsession
    dbsession = xivo_connect()


def xivo_session():
    global dbsession
    if not dbsession:
        dbsession = xivo_connect()
    return dbsession


def _execute_with_xivo_session(func, *args, **kwargs):
    sess = xivo_session()
    result = func(sess, *args, **kwargs)
    sess.commit()
    return result


def xivo_daosession(func):

    @wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return _execute_with_xivo_session(func, *args, **kwargs)
        except (OperationalError, InvalidRequestError):
            logger.info("Trying to reconnect")
            xivo_reconnect()
            return _execute_with_xivo_session(func, *args, **kwargs)

    return wrapped


@xivo_daosession
def get_password(session, login):
    result = session.query(AccessWebService).filter(and_(AccessWebService.login == login,
                                                         AccessWebService.disable == 0)).first()
    if result == None:
        return None
    else:
        return result.passwd


@xivo_daosession
def get_allowed_hosts(session):
    result = session.query(distinct(AccessWebService.host)).filter(and_(AccessWebService.host != None,
                                                                        AccessWebService.disable == 0)).all()
    result = [item[0].encode('utf-8', 'ignore') for item in result]
    logger.debug("Allowed hosts: " + str(result))
    return result
