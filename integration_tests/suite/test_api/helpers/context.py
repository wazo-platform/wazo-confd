import random
import string

from test_api.database import create_helper as db_helper


def new_context(context=None, type_='internal'):
    context = context or 'ctx_' + ''.join(random.choice(string.ascii_letters) for _ in range(10))
    db = db_helper()
    with db.queries() as queries:
        queries.insert_context(context, type_)
    return context


def generate_context(context=None, type_='internal'):
    context = new_context(context, type_)
    return {'name': context,
            'id': context,
            'type': type_}


def delete_context(context, check=False):
    db = db_helper()
    with db.queries() as queries:
        queries.delete_context(context)
