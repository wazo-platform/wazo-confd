# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for

from xivo_dao.alchemy.phone_number import PhoneNumber

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import PhoneNumberSchema


class PhoneNumberList(ListResource):
    model = PhoneNumber
    schema = PhoneNumberSchema

    def build_headers(self, resource):
        return {
            'Location': url_for(
                'phone_numbers', uuid=str(resource.uuid), _external=True
            ),
        }

    @required_acl('confd.phone-numbers.read')
    def get(self):
        return super().get()

    @required_acl('confd.phone-numbers.create')
    def post(self):
        return super().post()


class PhoneNumberItem(ItemResource):
    schema = PhoneNumberSchema
    has_tenant_uuid = True

    @required_acl('confd.phone-numbers.{uuid}.read')
    def get(self, uuid):
        return super().get(uuid)

    @required_acl('confd.phone-numbers.{uuid}.update')
    def put(self, uuid):
        return super().put(uuid)

    @required_acl('confd.phone-numbers.{uuid}.delete')
    def delete(self, uuid):
        return super().delete(uuid)
