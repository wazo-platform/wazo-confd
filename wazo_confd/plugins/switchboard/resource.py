# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request, url_for
from xivo_dao.alchemy.switchboard import Switchboard
from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ItemResource, ListResource

from .schema import SwitchboardSchema


class _BaseSwitchboardResource:
    def __init__(self, service, moh_dao):
        super().__init__(service)
        self._moh_dao = moh_dao

    def _update_moh_fields(self, form, tenant_uuids):
        if 'queue_music_on_hold' in form:
            form['queue_moh_uuid'] = self._find_moh_uuid(
                form, 'queue_music_on_hold', tenant_uuids
            )

        if 'waiting_room_music_on_hold' in form:
            form['hold_moh_uuid'] = self._find_moh_uuid(
                form, 'waiting_room_music_on_hold', tenant_uuids
            )

        return form

    def _find_moh_uuid(self, form, field, tenant_uuids):
        name = form.pop(field, None)
        if name:
            try:
                moh = self._moh_dao.get_by(name=name, tenant_uuids=tenant_uuids)
            except NotFoundError:
                raise errors.param_not_found(field, 'moh')
            return moh.uuid


class SwitchboardList(_BaseSwitchboardResource, ListResource):
    model = Switchboard
    schema = SwitchboardSchema

    def build_headers(self, switchboard):
        return {
            'Location': url_for('switchboards', uuid=switchboard.uuid, _external=True)
        }

    @required_acl('confd.switchboards.create')
    def post(self):
        form = self.schema().load(request.get_json())
        form = self.add_tenant_to_form(form)
        form = self._update_moh_fields(form, tenant_uuids=[form['tenant_uuid']])
        model = self.model(**form)
        model = self.service.create(model)
        return self.schema().dump(model), 201, self.build_headers(model)

    @required_acl('confd.switchboards.read')
    def get(self):
        return super().get()


class SwitchboardItem(_BaseSwitchboardResource, ItemResource):
    schema = SwitchboardSchema
    has_tenant_uuid = True

    @required_acl('confd.switchboards.{uuid}.read')
    def get(self, uuid):
        return super().get(uuid)

    @required_acl('confd.switchboards.{uuid}.update')
    def put(self, uuid):
        return super().put(uuid)

    def parse_and_update(self, model, **kwargs):
        form = self.schema().load(request.get_json(), partial=True)
        form = self._update_moh_fields(form, tenant_uuids=[model.tenant_uuid])
        updated_fields = self.find_updated_fields(model, form)
        for name, value in form.items():
            setattr(model, name, value)
        self.service.edit(model, updated_fields=updated_fields, **kwargs)

    @required_acl('confd.switchboards.{uuid}.delete')
    def delete(self, uuid):
        return super().delete(uuid)
