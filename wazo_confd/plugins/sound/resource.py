# Copyright 2017-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request, url_for
from wazo.tenant_flask_helpers import Tenant

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource, ItemResource, ListResource

from .model import SoundCategory, SoundFile, SoundFormat
from .schema import SoundSchema, SoundQueryParametersSchema


class SoundList(ListResource):
    model = SoundCategory
    schema = SoundSchema
    has_tenant_uuid = True

    def build_headers(self, sound):
        return {'Location': url_for('sounds', category=sound.name, _external=True)}

    @required_acl('confd.sounds.create')
    def post(self):
        return super().post()

    @required_acl('confd.sounds.read')
    def get(self):
        return super().get()


class SoundItem(ItemResource):
    schema = SoundSchema
    has_tenant_uuid = True

    @required_acl('confd.sounds.{category}.read')
    def get(self, category):
        tenant = Tenant.autodetect()
        model = self.service.get(tenant.uuid, category)
        return self.schema().dump(model)

    @required_acl('confd.sounds.{category}.delete')
    def delete(self, category):
        tenant = Tenant.autodetect()
        model = self.service.get(tenant.uuid, category)
        self.service.delete(model)
        return '', 204

    def put(self, category):
        return '', 405


class SoundFileItem(ConfdResource):
    has_tenant_uuid = True

    def __init__(self, service):
        self.service = service

    @required_acl('confd.sounds.{category}.files.{filename}.read')
    def get(self, category, filename):
        tenant = Tenant.autodetect()
        parameters = SoundQueryParametersSchema().load(request.args)
        parameters['file_name'] = filename
        sound = self.service.get(tenant.uuid, category, parameters)
        response = self.service.load_first_file(sound)
        return response

    @required_acl('confd.sounds.{category}.files.{filename}.update')
    def put(self, category, filename):
        tenant = Tenant.autodetect()
        parameters = SoundQueryParametersSchema().load(request.args)
        sound = self.service.get(tenant.uuid, category, with_files=False)
        sound_file = SoundFile(
            name=filename,
            formats=[
                SoundFormat(
                    format_=parameters.get('format'),
                    language=parameters.get('language'),
                )
            ],
        )
        sound.files = [sound_file]
        self.service.save_first_file(sound, request.data)
        return '', 204

    @required_acl('confd.sounds.{category}.files.{filename}.delete')
    def delete(self, category, filename):
        tenant = Tenant.autodetect()
        parameters = SoundQueryParametersSchema().load(request.args)
        parameters['file_name'] = filename
        sound = self.service.get(tenant.uuid, category, parameters)
        self.service.delete_files(sound)
        return '', 204
