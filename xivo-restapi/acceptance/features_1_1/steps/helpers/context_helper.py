from helpers.remote import remote_exec


def create_context(context_name):
    remote_exec(_create_context, name=context_name)


def _create_context(channel, name):
    from xivo_dao.data_handler.context import services as context_services
    from xivo_dao.data_handler.context.model import Context, ContextType

    existing_context = context_services.find_by_name(name)
    if not existing_context:
        context = Context(name=name, display_name=name, type=ContextType.internal)
        context_services.create(context)
