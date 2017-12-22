# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields
from marshmallow.validate import Length, NoneOf, Regexp

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink

from .storage import RESERVED_FOLDERS

ASTERISK_CATEGORY = 'system'
RESERVED_FOLDERS_ERROR = "The following name are reserved for internal usage: {}".format(RESERVED_FOLDERS)
FOLDER_REGEX = r'^[a-zA-Z0-9]{1}[-_.a-zA-Z0-9]+$'


class SoundFileSchema(BaseSchema):
    name = fields.String()


class SoundSchema(BaseSchema):
    name = fields.String(validate=[Length(max=149, min=1),
                                   NoneOf([ASTERISK_CATEGORY]),
                                   NoneOf(RESERVED_FOLDERS, error=RESERVED_FOLDERS_ERROR),
                                   Regexp(FOLDER_REGEX)],
                         required=True)
    files = fields.Nested(SoundFileSchema, many=True, dump_only=True)

    links = ListLink(Link('sounds', field='name'))
