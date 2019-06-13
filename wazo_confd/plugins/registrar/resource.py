# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for
from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource

from .model import Registrar
from .schema import RegistrarSchema


class RegistrarList(ListResource):

    model = Registrar.from_args
    schema = RegistrarSchema

    def build_headers(self, registrar):
        return {'Location': url_for('registrars', id=registrar.id, _external=True)}

    @required_acl('confd.registrars.read')
    def get(self):
        return super(RegistrarList, self).get()

    @required_acl('confd.registrars.create')
    def post(self):
        return super(RegistrarList, self).post()
