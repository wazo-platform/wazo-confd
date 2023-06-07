# Copyright 2017-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import io
import logging
import wave

from marshmallow import fields, pre_load, validates
from marshmallow.exceptions import ValidationError
from marshmallow.validate import Length, OneOf

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink, Nested

logger = logging.getLogger(__name__)


class MohFileSchema(BaseSchema):
    name = fields.String()


class MohSchema(BaseSchema):
    uuid = fields.UUID(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    name = fields.String(dump_only=True)
    label = fields.String(validate=Length(max=128), required=True)
    mode = fields.String(validate=OneOf(['custom', 'files', 'mp3']), required=True)
    application = fields.String(validate=Length(max=256), allow_none=True)
    sort = fields.String(
        validate=OneOf(['alphabetical', 'random', 'random_start']), allow_none=True
    )
    files = Nested(MohFileSchema, many=True, dump_only=True)

    links = ListLink(Link('moh', field='uuid'))

    # DEPRECATED 21.15
    @pre_load
    def copy_name_to_label(self, data, **kwargs):
        if 'label' in data:
            return data
        if 'name' in data:
            logger.warning('the "name" field of moh is deprecated. use "label" instead')
            data['label'] = data['name']
        return data


class MohSchemaPUT(MohSchema):
    name = fields.String(dump_only=True)


class MohFileUploadSchema(BaseSchema):
    wav_file = fields.Raw()

    @pre_load
    def wrap_binary(self, data, **kwargs):
        return {'wav_file': data}

    @validates('wav_file')
    def validate_moh(self, data, **kwargs):
        wav_stream = io.BytesIO(data)
        try:
            with wave.open(wav_stream, 'rb') as f:
                if f.getnchannels() > 1:
                    raise ValidationError('Audio file should be mono')
                if f.getframerate() != 8000 and f.getframerate() != 16000:
                    raise ValidationError(
                        'Audio file should have a sample rate of 8kHz or 16kHz'
                    )
                if f.getsampwidth() > 2:
                    raise ValidationError(
                        'Audio file should have bit depth of no more than 16 bits'
                    )
        except wave.Error as e:
            raise ValidationError(f'Not able to read audio file: "{e}"')
