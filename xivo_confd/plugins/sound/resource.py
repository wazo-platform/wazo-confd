# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import request
from flask import url_for

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ConfdResource, ItemResource, ListResource

from .model import SoundCategory
from .schema import SoundSchema


class SoundList(ListResource):

    model = SoundCategory
    schema = SoundSchema

    def build_headers(self, sound):
        return {'Location': url_for('sounds', name=sound.name, _external=True)}

    @required_acl('confd.sounds.create')
    def post(self):
        return super(SoundList, self).post()

    @required_acl('confd.sounds.read')
    def get(self):
        return super(SoundList, self).get()


class SoundItem(ItemResource):

    schema = SoundSchema

    @required_acl('confd.sounds.{name}.read')
    def get(self, name):
        return super(SoundItem, self).get(name)

    @required_acl('confd.sounds.{name}.delete')
    def delete(self, name):
        return super(SoundItem, self).delete(name)

    def put(self, name):
        return '', 405


class SoundFileItem(ConfdResource):

    def __init__(self, service):
        self.service = service

    @required_acl('confd.sounds.{name}.files.{filename}.read')
    def get(self, name, filename):
        sounds = self.service.get(name)
        response = self.service.load_file(sounds, filename)
        return response

    @required_acl('confd.sounds.{name}.files.{filename}.update')
    def put(self, name, filename):
        sounds = self.service.get(name)
        self.service.save_file(sounds, filename, request.data)
        return '', 204

    @required_acl('confd.sounds.{name}.files.{filename}.delete')
    def delete(self, name, filename):
        sounds = self.service.get(name)
        self.service.delete_file(sounds, filename)
        return '', 204
