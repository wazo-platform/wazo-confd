from test_api import confd

FAKE_ID = 999999999


def test_get_fake_func_key():
    response = confd.func_keys(FAKE_ID).get()
    response.assert_status(404)
