# -*- coding: UTF-8 -*-
#
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
from functools import wraps
from sqlalchemy.exc import OperationalError, InvalidRequestError
from xivo_dao.helpers.db_manager import session, reconnect


def _execute_with_session_class(self_holder, func, *args, **kwargs):
    sess = session()
    result = func(self_holder, sess, *args, **kwargs)
    sess.commit()
    return result


def daosession_class(func):

    @wraps(func)
    def wrapped(self_holder, *args, **kwargs):
        try:
            return _execute_with_session_class(self_holder,
                                               func,
                                               *args,
                                               **kwargs)

        except (OperationalError, InvalidRequestError):
            reconnect()
            return _execute_with_session_class(self_holder,
                                               func,
                                               *args,
                                               **kwargs)

    return wrapped
