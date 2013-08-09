from acceptance.features_1_1 import ws_utils_session as ws_utils

EXTENSIONS_URL = 'extensions'


def all_extensions():
    return ws_utils.rest_get(EXTENSIONS_URL)


def get_extension(extension_id):
    return ws_utils.rest_get('%s/%s' % (EXTENSIONS_URL, extension_id))


def create_extension(properties):
    return ws_utils.rest_post(EXTENSIONS_URL, properties)


def delete_extension(extension_id):
    return ws_utils.rest_delete('%s/%s' % (EXTENSIONS_URL, extension_id))
