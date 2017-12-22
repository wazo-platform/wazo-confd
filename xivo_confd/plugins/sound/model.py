# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+


class SoundCategory(object):

    def __init__(self, name=None, files=None):
        self.name = name
        self.files = files if files else []


class SoundFile(object):

    def __init__(self, name=None, formats=None):
        self.name = name
        self.formats = formats if formats else []


class SoundFormat(object):

    def __init__(self, format_=None, language=None, text=None):
        self.format = format_
        self.language = language
        self.text = text
