# Copyright 2017-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import io
import wave

from marshmallow.exceptions import ValidationError

from xivo_dao.helpers import errors
from xivo_dao.resources.moh import dao as moh_dao

from wazo_confd.helpers.validator import UniqueField, Validator, ValidationGroup


class MohModelValidator(Validator):
    def validate(self, moh):
        if moh.mode == 'custom' and moh.application is None:
            raise errors.moh_custom_no_app()


class MohFileValidator(Validator):
    def validate(self, moh_file):
        moh_filestream = io.BytesIO(moh_file)
        try:
            with wave.open(moh_filestream, 'rb') as wav_file:
                if wav_file.getnchannels() > 1:
                    raise ValidationError('WAV file must be mono')
                if wav_file.getsampwidth() > 2:
                    raise ValidationError(
                        'WAV file sample width must be at maximum 16 bits.'
                    )
                if wav_file.getframerate() != 8000:
                    raise ValidationError('WAV file sample rate must be 8kHz')
        except wave.Error:
            raise ValidationError(
                'Cannot open WAV file. Must not be in the right format.'
            )


def build_validator():
    moh_validator = MohModelValidator()
    validation_group = ValidationGroup(
        create=[
            UniqueField('name', lambda name: moh_dao.find_by(name=name), 'MOH'),
            moh_validator,
        ],
        edit=[moh_validator],
    )

    return validation_group
