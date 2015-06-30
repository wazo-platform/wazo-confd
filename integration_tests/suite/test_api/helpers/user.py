from test_api import confd


def add_user(**params):
    response = confd.users.post(params)
    return response.item


def delete_user(user_id, check=False):
    response = confd.users(user_id).delete()
    if check:
        response.assert_ok()


def generate_user(**params):
    params.setdefault('firstname', 'John')
    params.setdefault('lastname', 'Doe')
    return add_user(**params)
