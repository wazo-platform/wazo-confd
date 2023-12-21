# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask_restful import abort

from wazo_confd.database import wizard as wizard_db


def wazo_unconfigured(func):
    def wrapper(*args, **kwargs):
        if wizard_db.get_wazo_configured().configured:
            abort(403, message='Wazo is already configured')
        return func(*args, **kwargs)

    return wrapper
