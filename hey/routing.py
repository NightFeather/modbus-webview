from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url
from django.core.asgi import get_asgi_application

from hey.consumers import ModbusPoller

application = ProtocolTypeRouter({
  # (http->django views is added by default)
  'websocket': AuthMiddlewareStack(
    URLRouter(
      [
           url(r'^sock/$', ModbusPoller)
      ]
    )
  ),
})
