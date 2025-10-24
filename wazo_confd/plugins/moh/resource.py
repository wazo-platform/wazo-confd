# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from uuid import uuid4

from flask import request, url_for
from xivo_dao.alchemy.moh import MOH

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource, ItemResource, ListResource

from .schema import MohFileUploadSchema, MohSchema, MohSchemaPUT


class MohList(ListResource):
    model = MOH
    schema = MohSchema
    moh_name_fmt = 'moh-{tenant_slug}-{moh_uuid}'

    def __init__(self, tenant_dao, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tenant_dao = tenant_dao

    def build_headers(self, moh):
        return {'Location': url_for('moh', uuid=moh.uuid, _external=True)}

    @required_acl('confd.moh.create')
    def post(self):
        form = self.schema().load(request.get_json(force=True))
        form = self.add_tenant_to_form(form)

        tenant = self._tenant_dao.get(form['tenant_uuid'])
        form['uuid'] = uuid4()
        form['name'] = self.moh_name_fmt.format(
            tenant_slug=tenant.slug,
            moh_uuid=form['uuid'],
        )

        model = self.model(**form)
        model = self.service.create(model)
        return self.schema().dump(model), 201, self.build_headers(model)

    @required_acl('confd.moh.read')
    def get(self):
        return super().get()


class MohItem(ItemResource):
    schema = MohSchemaPUT
    has_tenant_uuid = True

    @required_acl('confd.moh.{uuid}.read')
    def get(self, uuid):
        return super().get(uuid)

    @required_acl('confd.moh.{uuid}.update')
    def put(self, uuid):
        return super().put(uuid)

    @required_acl('confd.moh.{uuid}.delete')
    def delete(self, uuid):
        return super().delete(uuid)


class MohFileItem(ConfdResource):
    schema = MohFileUploadSchema
    has_tenant_uuid = True

    def __init__(self, service):
        self.service = service

    @required_acl('confd.moh.{uuid}.files.{filename}.read')
    def get(self, uuid, filename):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        moh = self.service.get(uuid, tenant_uuids=tenant_uuids)
        response = self.service.load_file(moh, filename)
        return response

    @required_acl('confd.moh.{uuid}.files.{filename}.update')
    def put(self, uuid, filename):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        moh = self.service.get(uuid, tenant_uuids=tenant_uuids)
        uploaded_file = request.data
        if moh.mode == 'files':
            uploaded_file = self.schema().load(uploaded_file)['wav_file']
        self.service.save_file(moh, filename, uploaded_file)
        return '', 204

    @required_acl('confd.moh.{uuid}.files.{filename}.delete')
    def delete(self, uuid, filename):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        moh = self.service.get(uuid, tenant_uuids=tenant_uuids)
        self.service.delete_file(moh, filename)
        return '', 204
