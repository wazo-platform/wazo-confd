# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class MiddleWareHandle:
    def __init__(self):
        self._middlewares = {}

    def register(self, resource_name, middleware):
        self._middlewares[resource_name] = middleware

    def get(self, resource_name):
        return self._middlewares[resource_name]
