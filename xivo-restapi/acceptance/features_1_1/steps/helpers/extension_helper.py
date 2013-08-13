from helpers.remote import remote_exec


def delete_all():
    remote_exec(_delete_all)


def _delete_all(channel):
    from xivo_dao.data_handler.extension import services as extension_services
    from xivo_dao.data_handler.user_line_extension import services as ule_services

    hidden_extensions = extension_services.find_all(commented=True)
    visible_extensions = extension_services.find_all()

    extensions = [e for e in hidden_extensions + visible_extensions if e.context != 'xivo-features']

    for extension in extensions:

        ules = ule_services.find_all_by_extension_id(extension.id)
        for ule in ules:
            ule_services.delete(ule)

        extension_services.delete(extension)


def create_extensions(extensions):
    extensions = [dict(e) for e in extensions]
    remote_exec(_create_extensions, extensions=extensions)


def _create_extensions(channel, extensions):
    from xivo_dao.data_handler.extension import services as extension_services
    from xivo_dao.data_handler.extension.model import Extension

    for extinfo in extensions:
        extension = Extension(**extinfo)
        extension_services.create(extension)
