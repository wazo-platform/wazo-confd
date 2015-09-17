from test_api import confd
from test_api import config
from test_api.helpers.context import new_context


def generate_voicemail(**kwargs):
    kwargs.setdefault('name', 'myvoicemail')
    kwargs.setdefault('number', find_available_number(config.CONTEXT))
    kwargs.setdefault('context', config.CONTEXT)
    return add_voicemail(**kwargs)


def generate_number_and_context():
    number = find_available_number(config.CONTEXT)
    return number, config.CONTEXT


def new_number_and_context(context):
    new_context(context)
    return find_available_number(context), context


def find_available_number(context=config.CONTEXT):
    response = confd.voicemails.get()
    numbers = [int(v['number'])
               for v in response.items
               if v['context'] == context and v['number'].isdigit()]

    available_numbers = set(config.EXTENSION_RANGE) - set(numbers)
    return str(available_numbers.pop())


def add_voicemail(**params):
    response = confd.voicemails.post(params)
    return response.item


def delete_voicemail(voicemail_id, check=False):
    response = confd.voicemails(voicemail_id).delete()
    if check:
        response.assert_ok()
