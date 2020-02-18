# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.rest_api_helpers import APIException


class PJSIPDocError(APIException):
    def __init__(self, msg):
        super().__init__(400, msg, None, None, None)
