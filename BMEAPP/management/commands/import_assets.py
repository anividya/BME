import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand
from django.db import transaction
from BMEAPP.models import Asset  # Replace with your actual app name if different
from datetime import datetime


class Command(BaseCommand):
    help = 'Imports asset data from the "ASSET" sheet in the Excel file into the database'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        self.import_data(file_path)

    def import_data(self, file_path):
        # ✅ Read Excel data from 'ASSET' sheet
        try:
            df = pd.read_excel(file_path, sheet_name='ASSET')
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error reading Excel file: {e}'))
            return

        # ✅ Replace all string/null values and NaN with None
        df = df.replace(['NULL', 'null', 'Null', '', 'nan'], np.nan)
        df = df.where(pd.notnull(df), None)

        # ✅ Define expected date fields and formats
        date_columns = ['caldone', 'caldue', 'pmdone', 'pmdue', 'insdate']
        date_formats = ['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y']

        # ✅ Define fields you expect to import
        basic_fields = [
            'assetid', 'dept', 'assetname', 'asset_make', 'asset_model', 
            'slno', 'calvendor', 'caldur', 'calmonth', 'calstat',
            'pmdur', 'pmmonth', 'pmstat', 'asset_type'
        ]

        created = 0
        with transaction.atomic():
            for _, row in df.iterrows():
                if not row.get('assetid'):
                    continue  # skip rows without asset ID

                asset_data = {}

                # ✅ Assign normal fields
                for field in basic_fields:
                    if field in row and pd.notna(row[field]):
                        asset_data[field] = row[field]

                # ✅ Assign date fields with parsed values
                for date_field in date_columns:
                    value = row.get(date_field)
                    asset_data[date_field] = self.parse_date(value, date_formats)

                # ✅ Create Asset instance
                try:
                    Asset.objects.create(**asset_data)
                    created += 1
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Failed to create asset for row {row.get('assetid')}: {e}"))

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {created} assets'))

    def parse_date(self, value, formats):
        """Convert a date string or timestamp to a Python date object."""
        if pd.isna(value) or value is None:
            return None

        if isinstance(value, datetime) or isinstance(value, pd.Timestamp):
            return value.date()

        if isinstance(value, str):
            for fmt in formats:
                try:
                    return datetime.strptime(value.strip(), fmt).date()
                except ValueError:
                    continue

        return None  # If parsing fails
