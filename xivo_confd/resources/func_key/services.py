# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_dao.resources.func_key import dao
from xivo_dao.resources.func_key_template import dao as template_dao
from xivo_confd.resources.func_key import notifier
from xivo_dao.resources.func_key.model import UserFuncKey


def create_user_destination(user):
    func_key = UserFuncKey(user_id=user.id)
    created_func_key = dao.create(func_key)
    notifier.created(created_func_key)
    return created_func_key


def delete_user_destination(user):
    func_key = dao.find_user_destination(user.id)
    if func_key:
        template_dao.remove_func_key_from_templates(func_key)
        dao.delete(func_key)
        notifier.deleted(func_key)


def delete_bsfilter_destination(user):
    func_keys = dao.find_bsfilter_destinations_for_user(user.id)
    for func_key in func_keys:
        template_dao.remove_func_key_from_templates(func_key)
        dao.delete(func_key)
        notifier.deleted(func_key)


def find_all_fwd_unc(user_id):
    return _filter_fwd_type(user_id, 'unconditional')


def find_all_fwd_rna(user_id):
    return _filter_fwd_type(user_id, 'noanswer')


def find_all_fwd_busy(user_id):
    return _filter_fwd_type(user_id, 'busy')


def _filter_fwd_type(user_id, fwd_type):
    return [fwd.number or '' for fwd in dao.find_all_forwards(user_id, fwd_type)]
