# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import Session
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser
from xivo_dao.alchemy.func_key_mapping import FuncKeyMapping
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate


def find_all_dst_user(user_id):

    query = (Session.query(FuncKeyTemplate)
             .join(FuncKeyMapping, FuncKeyTemplate.id == FuncKeyMapping.template_id)
             .join(FuncKey, FuncKeyMapping.func_key_id == FuncKey.id)
             .join(FuncKeyDestUser, FuncKey.id == FuncKeyDestUser.func_key_id)
             .filter(FuncKeyDestUser.user_id == user_id)
             )

    return query.all()
