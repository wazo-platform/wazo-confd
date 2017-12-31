# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+


class SoundCategory(object):

    def __init__(self, name=None, files=None):
        self.name = name
        self.files = files if files else []

    def add_file(self, new_file):
        for file_ in self.files:
            if file_.name == new_file.name:
                file_.update(new_file)
                break
        else:
            self.files.append(new_file)


class SoundFile(object):

    def __init__(self, name=None, formats=None):
        self.name = name
        self.formats = formats if formats else []

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

    def __init__(self, format_=None, language=None, text=None, path=None):
        self.format = format_
        self.language = language
        self.text = text
        self.path = path

    def __eq__(self, other):
        return (self.format == other.format and
                self.language == other.language and
                self.text == other.text and
                self.path == other.path)
