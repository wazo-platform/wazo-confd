# -*- coding: utf-8 -*-
# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class SoundCategory(object):

    has_tenant_uuid = True

    def __init__(self, name=None, files=None, tenant_uuid=None):
        self.name = name
        self.files = files if files else []
        self.tenant_uuid = tenant_uuid

    def add_file(self, new_file):
        for file_ in self.files:
            if file_.name == new_file.name:
                file_.update(new_file)
                break
        else:
            self.files.append(new_file)

    def __str__(self):
        return ('SoundCategory(tenant_uuid={tenant_uuid}, name={name}, files=<{file_count}>)'
                .format(tenant_uuid=self.tenant_uuid,
                        name=self.name,
                        file_count=len(self.files)))


class SoundFile(object):

    has_tenant_uuid = True

    def __init__(self, name=None, formats=None, tenant_uuid=None):
        self.name = name
        self.formats = formats if formats else []
        self.tenant_uuid = tenant_uuid

    def update(self, other_file):
        if other_file.name != self.name:
            return
        self._update_formats(other_file.formats)

    def _update_formats(self, other_formats):
        new_formats = []
        for other_format in other_formats:
            for format_ in self.formats:
                if other_format == format_:
                    break
            else:
                new_formats.append(other_format)
        self.formats = self.formats + new_formats


class SoundFormat(object):

    has_tenant_uuid = True

    extension_map = {
        'wav': 'slin',
    }
    format_map = {v: k for k, v in extension_map.iteritems()}

    def __init__(self, format_=None, language=None, text=None, path=None, extension=None, tenant_uuid=None):
        if format_ is not None:
            self.format = format_
        else:
            self.extension = extension
        self.language = language
        self.text = text
        self.path = path
        self.tenant_uuid = tenant_uuid

    def __eq__(self, other):
        return (self.format == other.format
                and self.language == other.language
                and self.text == other.text
                and self.path == other.path)

    @property
    def extension(self):
        if self.format is None:
            return ''
        return self.format_map.get(self.format, self.format)

    @extension.setter
    def extension(self, value):
        if value == '':
            self.format = None
        else:
            self.format = self.extension_map.get(value, value)
