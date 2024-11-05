# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for, request

from xivo_dao.alchemy.phone_number import PhoneNumber

from xivo.tenant_flask_helpers import Tenant
from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource, ListResource, ItemResource

from .schema import (
    PhoneNumberSchema,
    phone_number_range_spec_schema,
    phone_number_list_schema,
    phone_number_main_spec_schema,
    phone_number_schema,
)
from .service import PhoneNumberService


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


class PhoneNumberRange(ConfdResource):
    def __init__(self, service: PhoneNumberService):
        self.service = service
        super().__init__()

    @required_acl('confd.phone-numbers.create')
    def post(self):
        tenant_uuid = Tenant.autodetect().uuid
        range_spec = phone_number_range_spec_schema.load(request.get_json())
        new_phone_numbers, old_phone_numbers = self.service.create_range(
            range_spec, tenant_uuid=tenant_uuid
        )
        return (
            phone_number_list_schema.dump(
                {
                    'created': new_phone_numbers,
                    'links': new_phone_numbers + old_phone_numbers,
                    'total': len(new_phone_numbers) + len(old_phone_numbers),
                }
            ),
            201,
        )


class PhoneNumberMain(ConfdResource):
    def __init__(self, service: PhoneNumberService):
        self.service = service
        super().__init__()

    def build_headers(self, resource):
        return {
            'Location': url_for(
                'phone_numbers', uuid=str(resource.uuid), _external=True
            ),
        }

    @required_acl('confd.phone-numbers.main.read')
    def get(self):
        tenant_uuid = Tenant.autodetect().uuid
        main = self.service.get_main(tenant_uuid)
        return (phone_number_schema.dump(main), 200)

    @required_acl('confd.phone-numbers.main.update')
    def put(self):
        tenant_uuid = Tenant.autodetect().uuid
        main_spec = phone_number_main_spec_schema.load(request.get_json())
        new_main_number = self.service.update_main(main_spec, tenant_uuid)
        return (None, 204, self.build_headers(new_main_number))


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
