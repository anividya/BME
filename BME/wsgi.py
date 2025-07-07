import os
from django.core.wsgi import get_wsgi_application

# Set the default settings module for the 'DJANGO_SETTINGS_MODULE' environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BME.settings')

# Get the WSGI application for serving the Django app
application = get_wsgi_application()
