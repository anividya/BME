start cmd /k "celery -A BME worker --loglevel=info"
start cmd /k "celery -A BME beat --loglevel=info"