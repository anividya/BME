cd /d D:\R&D\New_DJANGO
call env\Scripts\activate
waitress-serve --host=127.0.0.1 --port=8000 BME.wsgi:application
pause