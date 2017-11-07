# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+


from xivo_dao.helpers.db_manager import Session
from xivo_dao.helpers import errors

from xivo_dao.alchemy.pickup import Pickup


def find_by(**criteria):
    query = _find_query(criteria)
    return query.first()


def _find_query(criteria):
    query = Session.query(Pickup)
    for name, value in criteria.iteritems():
        column = getattr(Pickup, name, None)
        if not column:
            raise errors.unknown(name)
        query = query.filter(column == value)
    return query
