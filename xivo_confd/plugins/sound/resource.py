# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import request
from flask import url_for

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ConfdResource, ItemResource, ListResource

from .model import SoundCategory, SoundFile, SoundFormat
from .schema import SoundSchema, SoundQueryParametersSchema


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
        # XXX extract query string
        sounds = self.service.get(name)
        response = self.service.load_first_file(sound)
        return response

    @required_acl('confd.sounds.{name}.files.{filename}.update')
    def put(self, name, filename):
        # XXX extract query string
        # XXX call exists instead get to avoid getting all files
        sound = self.service.get(name)
        sound_file = SoundFile(
            name=filename,
        )
        sound.files = [sound_file]
        self.service.save_first_file(sound, request.data)
        return '', 204

    @required_acl('confd.sounds.{name}.files.{filename}.delete')
    def delete(self, name, filename):
        # XXX extract query string
        sounds = self.service.get(name)
        self.service.delete_files(sound)
        return '', 204
