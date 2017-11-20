# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from werkzeug.routing import BaseConverter, ValidationError


class FilenameConverter(BaseConverter):

    def to_python(self, value):
        if not value or len(value) > 194:
            raise ValidationError()
        if u'/' in value or value.startswith(u'.'):
            raise ValidationError()
        return value
