# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from xivo_dao.alchemy.staticvoicemail import StaticVoicemail
from xivo_dao.helpers.db_manager import Session


def find_all_timezone():
    rows = (
        Session.query(StaticVoicemail.var_name)
        .filter(StaticVoicemail.category == 'zonemessages')
        .all()
    )

    return [row.var_name for row in rows]
