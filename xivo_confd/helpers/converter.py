# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from werkzeug.routing import BaseConverter, ValidationError


class FilenameConverter(BaseConverter):

    def to_python(self, value):
        if not value or len(value) > 194:
            raise ValidationError()
        if '/' in value or value.startswith('.'):
            raise ValidationError()
        return value
