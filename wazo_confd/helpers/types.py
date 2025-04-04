from collections.abc import Callable
from typing import Any, TypedDict

from flask_restful import Api
from wazo_auth_client import Client as AuthClient
from xivo.status import StatusAggregator
from xivo.token_renewer import Callback

from wazo_confd._bus import BusConsumer, BusPublisher
from wazo_confd.helpers.asterisk import PJSIPDoc
from wazo_confd.helpers.middleware import MiddleWareHandle

TokenChangedSubscribeCallback = Callable[[Callback], None]


class PluginDependencies(TypedDict):
    api: Api
    config: dict[str, Any]
    token_changed_subscribe: TokenChangedSubscribeCallback
    bus_consumer: BusConsumer
    bus_publisher: BusPublisher
    auth_client: AuthClient
    middleware_handle: MiddleWareHandle
    pjsip_doc: PJSIPDoc
    status_aggregator: StatusAggregator
