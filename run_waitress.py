from waitress import serve
from BME.wsgi import application  # This imports your WSGI app

if __name__ == '__main__':
    serve(application, host='0.0.0.0', port=8000, threads=8)
