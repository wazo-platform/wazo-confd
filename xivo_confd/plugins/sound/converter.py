# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .model import SoundFile, SoundFormat


def convert_ari_sounds_to_model(sounds):
    result = []
    for sound in sounds:
        sound_file = SoundFile(name=sound.get('id'))
        for format_ in sound.get('formats'):
            sound_format = SoundFormat(
                format_=format_.get('format'),
                language=format_.get('language'),
                text=sound.get('text') if format_.get('language') in ['en', 'en_US'] else None,
            )
            sound_file.formats.append(sound_format)
        result.append(sound_file)
    return result
