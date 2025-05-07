# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .. import config
from . import confd
from .context import generate_context


def generate_voicemail(**kwargs):
    kwargs.setdefault('name', 'myvoicemail')
    kwargs.setdefault('number', find_available_number(config.CONTEXT))
    kwargs.setdefault('context', config.CONTEXT)
    return add_voicemail(**kwargs)


def generate_number_and_context():
    number = find_available_number(config.CONTEXT)
    return number, config.CONTEXT


def new_number_and_context(context_label):
    context = generate_context(label=context_label)
    return find_available_number(context['name']), context['name']


def find_available_number(context=config.CONTEXT, exclude=None):
    exclude = {int(n) for n in exclude} if exclude else set()
    response = confd.voicemails.get()
    numbers = [
        int(v['number'])
        for v in response.items
        if v['context'] == context and v['number'].isdigit()
    ]

    available_numbers = set(config.USER_EXTENSION_RANGE) - set(numbers) - exclude
    return str(available_numbers.pop())


def add_voicemail(**params):
    response = confd.voicemails.post(params)
    return response.item


def delete_voicemail(voicemail_id, check=False, **params):
    response = confd.voicemails(voicemail_id).delete()
    if check:
        response.assert_ok()
