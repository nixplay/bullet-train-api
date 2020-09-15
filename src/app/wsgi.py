"""
WSGI config for app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""
import os
host_ip = os.environ.get('HOST_IP', 'localhost')
os.environ.setdefault("SIGNALFX_SERVICE_NAME", "bullet-train-api")
os.environ.setdefault("SIGNALFX_ENDPOINT_URL", ('http://%s:9080/v1/trace' % host_ip))

from signalfx_tracing import create_tracer, auto_instrument
auto_instrument(create_tracer())

from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.local")

application = get_wsgi_application()
application = DjangoWhiteNoise(application)
