# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import request, url_for

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ConfdResource, ItemResource, ListResource

from .model import SoundCategory, SoundFile, SoundFormat
from .schema import SoundSchema, SoundQueryParametersSchema


class SoundList(ListResource):

    model = SoundCategory
    schema = SoundSchema

    def build_headers(self, sound):
        return {'Location': url_for('sounds', category=sound.name, _external=True)}

    @required_acl('confd.sounds.create')
    def post(self):
        return super(SoundList, self).post()

    @required_acl('confd.sounds.read')
    def get(self):
        return super(SoundList, self).get()


class SoundItem(ItemResource):

    schema = SoundSchema

    @required_acl('confd.sounds.{category}.read')
    def get(self, category):
        return super(SoundItem, self).get(category)

    @required_acl('confd.sounds.{category}.delete')
    def delete(self, category):
        return super(SoundItem, self).delete(category)

    def put(self, category):
        return '', 405


class SoundFileItem(ConfdResource):

    def __init__(self, service):
        self.service = service

    @required_acl('confd.sounds.{category}.files.{filename}.read')
    def get(self, category, filename):
        parameters = SoundQueryParametersSchema().load(request.args).data
        parameters['file_name'] = filename
        sound = self.service.get(category, parameters)
        response = self.service.load_first_file(sound)
        return response

    @required_acl('confd.sounds.{category}.files.{filename}.update')
    def put(self, category, filename):
        parameters = SoundQueryParametersSchema().load(request.args).data
        sound = self.service.get(category, with_files=False)
        sound_file = SoundFile(
            name=filename,
            formats=[SoundFormat(format_=parameters.get('format'), language=parameters.get('language'))],
        )
        sound.files = [sound_file]
        self.service.save_first_file(sound, request.data)
        return '', 204

    @required_acl('confd.sounds.{category}.files.{filename}.delete')
    def delete(self, category, filename):
        parameters = SoundQueryParametersSchema().load(request.args).data
        parameters['file_name'] = filename
        sound = self.service.get(category, parameters)
        self.service.delete_files(sound)
        return '', 204
