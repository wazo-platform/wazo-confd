# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource


class PhoneNumberList(ListResource):
    def __init__(self):
        pass

    def build_headers(self, resource):
        return {}

    @required_acl('confd.phone-numbers.read')
    def get(self):
        return None

    @required_acl('confd.phone-numbers.create')
    def post(self):
        return None


class PhoneNumberItem(ItemResource):
    def __init__(self):
        pass

    @required_acl('confd.phone-numbers.{uuid}.read')
    def get(self, uuid):
        return None

    @required_acl('confd.phone-numbers.{uuid}.update')
    def put(self, uuid):
        return None

    @required_acl('confd.phone-numbers.{uuid}.delete')
    def delete(self, uuid):
        return None
