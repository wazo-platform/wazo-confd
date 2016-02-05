# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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

from xivo_dao.helpers.db_manager import Session
from xivo_dao.helpers import errors

from xivo_dao.alchemy.rightcall import RightCall
from xivo_dao.alchemy.rightcallmember import RightCallMember


def get_by(**criteria):
    query = find_query(criteria)
    row = query.first()
    if not row:
        raise errors.not_found('CallPermission', **criteria)
    return row


def find_all_by_member(member_type, member_id):
    query = (Session.query(RightCall)
             .join(RightCallMember,
                   RightCallMember.rightcallid == RightCall.id)
             .filter(RightCallMember.type == member_type)
             .filter(RightCallMember.typeval == str(member_id))
             )

    return query.all()


def find_query(criteria):
    query = Session.query(RightCall)
    for name, value in criteria.iteritems():
        column = getattr(RightCall, name, None)
        if not column:
            raise errors.unknown(name)
        query = query.filter(column == value)
    return query


def remove_user(user_id):
    query = (Session.query(RightCallMember)
             .filter_by(type='user',
                        typeval=str(user_id))
             )
    query.delete()


def associate_user(permission_id, user_id):
    member = RightCallMember(rightcallid=permission_id,
                             type='user',
                             typeval=str(user_id))
    Session.add(member)
