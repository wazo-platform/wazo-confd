# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import PJSIPDocList


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']

        api.add_resource(PJSIPDocList, '/asterisk/pjsip/doc')
