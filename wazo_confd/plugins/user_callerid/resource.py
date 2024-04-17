# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource


class UserCallerIDList(ListResource):
    ...
    # FIXME do not allow post method

    @required_acl('confd.users.{id}.callerids.outgoing')
    def get(self):
        ...
