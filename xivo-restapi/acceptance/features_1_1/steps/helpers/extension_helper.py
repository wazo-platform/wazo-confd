from helpers.remote import remote_exec


def delete_all():
    remote_exec(_delete_all)


def _delete_all(channel):
    from xivo_dao.data_handler.extension import services as extension_services

    extensions = [e for e in extension_services.find_all() if e.context != 'xivo-features']

    for extension in extensions:
        extension_services.delete(extension)
