# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class Plugin:
    def load(self, dependencies):
        _api = dependencies['api']
