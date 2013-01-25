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

from xivo_restapi.dao.helpers.dynamic_formatting import table_list_to_list_dict
from xivo_restapi.dao.exceptions import EmptyPageException,\
    InvalidPaginatorException


def get_paginated_data(session, query, paginator):
    if(type(paginator) != tuple or len(paginator) != 2\
       or type(paginator[0]) != int and type(paginator[1]) != int):
        raise InvalidPaginatorException("Invalid paginator provided. Expected tuple of 2 int")
    else:
        (page, page_size) = paginator
        if(page <= 0):
            raise InvalidPaginatorException("Invalid paginator provided: page number must be strictly positive")
        result = _get_data(session,
                         query,
                         query.offset((page - 1) * page_size).
                                            limit(page_size).all)
        if (result['total'] < (page - 1) * page_size and result['data'] == []):
            raise EmptyPageException()

        return result


def get_all_data(session, query):
    return _get_data(session, query, query.all)


def _get_data(session, query, fct):
    try:
        data = table_list_to_list_dict(fct())
        total = query.count()
    except Exception as e:
        session.rollback()
        #traitement de l'exception
        raise e

    return {'total': total,
            'data': data}

