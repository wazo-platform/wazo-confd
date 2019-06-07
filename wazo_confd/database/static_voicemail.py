# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0-or-later


from xivo_dao.helpers.db_manager import Session

from xivo_dao.alchemy.staticvoicemail import StaticVoicemail


def find_all_timezone():
    rows = (Session.query(StaticVoicemail.var_name)
            .filter(StaticVoicemail.category == 'zonemessages')
            .all())

    return [row.var_name for row in rows]
