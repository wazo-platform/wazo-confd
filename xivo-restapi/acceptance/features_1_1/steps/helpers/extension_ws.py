from acceptance.features_1_1 import ws_utils_session as ws_utils

EXTENSIONS_URL = 'extensions'


def all_extensions():
    return ws_utils.rest_get(EXTENSIONS_URL)


def get_extension(extension_id):
    return ws_utils.rest_get('%s/%s' % (EXTENSIONS_URL, extension_id))


def create_extension(parameters):
    return ws_utils.rest_post(EXTENSIONS_URL, parameters)


def update(extension_id, parameters):
    return ws_utils.rest_put('%s/%s' % (EXTENSIONS_URL, extension_id), parameters)


def delete_extension(extension_id):
    return ws_utils.rest_delete('%s/%s' % (EXTENSIONS_URL, extension_id))
