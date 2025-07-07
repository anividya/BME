from django.apps import AppConfig
import threading
import os

class BmeappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'BMEAPP'
