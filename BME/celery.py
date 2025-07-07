import os
from celery import Celery

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BME.settings')

# Create Celery app
app = Celery('BME')

# Load task modules from all registered Django apps
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks.py in apps
app.autodiscover_tasks()

#@app.task(bind=True)
#def debug_task(self):
    #print(f'Request: {self.request!r}')
