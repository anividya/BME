from django.core.management.base import BaseCommand
from BMEAPP.models import (
    Asset, InstallationDocument, PurchaseDocument, TrainigDocument,
    Workbook, WorkDocument, Gatepass, PRR, Departments
)
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Delete all records and media files associated with models'

    def delete_files_and_objects(self, queryset, file_fields):
        for obj in queryset:
            for field in file_fields:
                file = getattr(obj, field)
                if file and os.path.isfile(file.path):
                    os.remove(file.path)
            obj.delete()

    def handle(self, *args, **kwargs):
        # Delete files and objects
        self.delete_files_and_objects(InstallationDocument.objects.all(), ['document'])
        self.delete_files_and_objects(PurchaseDocument.objects.all(), ['document'])
        self.delete_files_and_objects(TrainigDocument.objects.all(), ['document'])
        self.delete_files_and_objects(Workbook.objects.all(), ['usersign', 'eng_sign', 'SR_report', 'invoice'])
        self.delete_files_and_objects(WorkDocument.objects.all(), ['document'])
        self.delete_files_and_objects(Gatepass.objects.all(), ['collector_sign', 'bme_sign', 'admin_sign'])
        self.delete_files_and_objects(PRR.objects.all(), ['User_Sign', 'BME_Sign', 'Admin_Sign'])

        # Delete models without media
        Asset.objects.all().delete()
        Departments.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('All data and associated media files have been deleted.'))
