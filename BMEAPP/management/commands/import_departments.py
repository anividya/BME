from django.core.management.base import BaseCommand
import pandas as pd
from BMEAPP.models import Departments  # Replace with your actual app name

class Command(BaseCommand):
    help = 'Import departments from the "dept" sheet in the Excel file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to Excel file')

    def handle(self, *args, file_path, **kwargs):
        try:
            # ✅ Specify the 'dept' sheet explicitly
            df = pd.read_excel(file_path, sheet_name='DEPT')

            for _, row in df.iterrows():
                Departments.objects.create(
                    LCNID=row['LCNID'],
                    LOCATION=row['LOCATION'],
                    PARENT_DEPT=row.get('PARENT_DEPT') or None
                )

            self.stdout.write(self.style.SUCCESS('Departments imported successfully.'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {e}'))
