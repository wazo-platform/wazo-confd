# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from flask_restful import abort
from xivo_confd.database import wizard as wizard_db


def xivo_unconfigured(func):
    def wrapper(*args, **kwargs):
        if wizard_db.get_xivo_configured().configured:
            abort(403, message=u'XiVO is already configured')
        return func(*args, **kwargs)
    return wrapper
