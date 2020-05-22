# Copyright 2019-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for
from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .model import Registrar
from .schema import RegistrarSchema


class RegistrarList(ListResource):

    model = Registrar.from_args
    schema = RegistrarSchema

    def build_headers(self, registrar):
        return {'Location': url_for('registrars', id=registrar.id, _external=True)}

    @required_acl('confd.registrars.read')
    def get(self):
        return super().get()

    @required_acl('confd.registrars.create')
    def post(self):
        return super().post()


class RegistrarItem(ItemResource):

    schema = RegistrarSchema

    @required_acl('confd.registrars.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.registrars.{id}.update')
    def put(self, id):
        return super().put(id)

    @required_acl('confd.registrars.{id}.delete')
    def delete(self, id):
        return super().delete(id)
