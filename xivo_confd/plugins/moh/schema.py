# -*- coding: UTF-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from marshmallow import fields
from marshmallow.validate import Length, OneOf

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink, AsteriskSection

# the regex is more restrictive since the name is used both for the Asterisk
# section and the directory on the file system
moh_name_validator = AsteriskSection(max_length=20, regex=r'^[a-zA-Z0-9][-_.a-zA-Z0-9]*$')


class MohFileSchema(BaseSchema):
    name = fields.String()


class MohSchema(BaseSchema):
    uuid = fields.UUID(dump_only=True)
    name = fields.String(validate=moh_name_validator, required=True)
    label = fields.String(validate=Length(max=128), allow_none=True)
    mode = fields.String(validate=OneOf(['custom', 'files', 'mp3']), required=True)
    application = fields.String(validate=Length(max=256), allow_none=True)
    sort = fields.String(validate=OneOf(['alphabetical', 'random', 'random_start']), allow_none=True)
    files = fields.Nested(MohFileSchema, many=True, dump_only=True)

    links = ListLink(Link('moh', field='uuid'))


class MohSchemaPUT(MohSchema):
    name = fields.String(dump_only=True)
