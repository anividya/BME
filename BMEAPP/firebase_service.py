# firebase_service.py
import firebase_admin
from firebase_admin import credentials, messaging
import os

class FirebaseService:
    _initialized = False

    @classmethod
    def initialize(cls):
        if not cls._initialized:
            try:
                firebase_admin.get_app()
            except ValueError:
                cred_path = os.path.join(os.path.dirname(__file__), 'firebase_credentials.json')
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                    cls._initialized = True
                else:
                    raise FileNotFoundError(f"Firebase credentials not found at {cred_path}")

    @classmethod
    def send_notification(cls, token, title, body):
        cls.initialize()
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=token
        )
        return messaging.send(message)