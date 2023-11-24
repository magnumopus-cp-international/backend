import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf import settings
from django.core.asgi import get_asgi_application

from config import routing
from summery_creator.common.channels import HeaderAuthMiddleware

if settings.DEBUG:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": HeaderAuthMiddleware(URLRouter(routing.websocket_urlpatterns)),
    }
)
