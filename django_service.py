import win32serviceutil
import win32service
import win32event
import os
from waitress import serve

class DjangoService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DjangoWaitressService"
    _svc_display_name_ = "Django Waitress Service"
    _svc_description_ = "Runs the Django application using the Waitress server."

    def __init__(self, args):
        super().__init__(args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.running = False
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BME.settings')
        from BME.wsgi import application  # Import your WSGI application here

        # Start Waitress server
        serve(application, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    win32serviceutil.HandleCommandLine(DjangoService)
