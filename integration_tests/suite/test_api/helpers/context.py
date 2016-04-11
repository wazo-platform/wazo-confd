import random
import string

from test_api import db


def generate_context(**parameters):
    name = 'ctx_' + ''.join(random.choice(string.ascii_letters) for _ in range(10))
    parameters.setdefault('name', name)
    parameters.setdefault('contexttype', 'internal')

    start = parameters.pop('start', None)
    end = parameters.pop('end', None)
    didlength = parameters.pop('didlength', 0)
    rangetype = parameters.pop('rangetype', 'user')

    with db.queries() as queries:
        id = queries.insert_context(**parameters)
        if start and end:
            queries.insert_context_range(id, rangetype, start, end, didlength)

    return {'name': id,
            'id': id,
            'type': parameters['contexttype']}


def delete_context(context, check=False):
    with db.queries() as queries:
        queries.delete_context(context)
