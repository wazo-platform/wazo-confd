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
    new_context(context, type_)
    return {'name': context,
            'type': type_}


def delete_context(context):
    db = db_helper()
    with db.queries() as queries:
        queries.delete_context(context)
