# Generated by Django 5.2.1 on 2025-06-22 05:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assetid', models.CharField(db_index=True, max_length=100, unique=True)),
                ('assetname', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('asset_make', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('asset_model', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('slno', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('dept', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('supplier', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('insdate', models.DateField(blank=True, db_index=True, null=True)),
                ('pmdone', models.DateField(blank=True, db_index=True, null=True)),
                ('pmdur', models.IntegerField(blank=True, db_index=True, null=True)),
                ('pmdue', models.DateField(blank=True, db_index=True, null=True)),
                ('pmmonth', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('LPMG', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('pmstat', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('caldue', models.DateField(blank=True, db_index=True, null=True)),
                ('caldur', models.IntegerField(blank=True, db_index=True, null=True)),
                ('caldone', models.DateField(blank=True, db_index=True, null=True)),
                ('calvendor', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('calmonth', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('LCALG', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('calstat', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('wrstart', models.DateField(blank=True, db_index=True, null=True)),
                ('wrend', models.DateField(blank=True, db_index=True, null=True)),
                ('warranty', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('mcstart', models.DateField(blank=True, db_index=True, null=True)),
                ('mcend', models.DateField(blank=True, db_index=True, null=True)),
                ('amc_cmc', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('LMCG', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('stat', models.CharField(blank=True, choices=[('ACTIVE', 'ACTIVE'), ('CONDEM', 'CONDEM'), ('RETURNED', 'RETURNED'), ('RENTAL', 'RENTAL')], db_index=True, max_length=100, null=True)),
                ('asset_type', models.CharField(blank=True, choices=[('CRITICAL', 'CRITICAL'), ('NON-CRITICAL', 'NON-CRITICAL'), ('MISCELLANEOUS', 'MISCELLANEOUS')], db_index=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Departments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('LCNID', models.CharField(max_length=100)),
                ('LOCATION', models.CharField(max_length=100)),
                ('PARENT_DEPT', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Gatepass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pass_id', models.CharField(max_length=100)),
                ('asset_name', models.CharField(blank=True, max_length=100, null=True)),
                ('collector_name', models.CharField(blank=True, max_length=100, null=True)),
                ('contact_num', models.CharField(blank=True, max_length=100, null=True)),
                ('sender_name', models.CharField(blank=True, max_length=100, null=True)),
                ('send_to', models.CharField(blank=True, max_length=100, null=True)),
                ('uoq', models.CharField(blank=True, max_length=100, null=True)),
                ('asset', models.CharField(blank=True, max_length=100, null=True)),
                ('serial', models.CharField(blank=True, max_length=100, null=True)),
                ('gatepasstype', models.CharField(blank=True, max_length=100, null=True)),
                ('qty', models.IntegerField(blank=True, null=True)),
                ('description', models.TextField(max_length=2000)),
                ('request_date', models.DateTimeField(blank=True, null=True)),
                ('out_date', models.DateTimeField(blank=True, null=True)),
                ('in_date', models.DateTimeField(blank=True, null=True)),
                ('collector_sign', models.ImageField(blank=True, null=True, upload_to='gpcollectorsign')),
                ('bme_sign', models.ImageField(blank=True, null=True, upload_to='gpbmesign')),
                ('admin_sign', models.ImageField(blank=True, null=True, upload_to='gpadminsign')),
                ('status', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PRR',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('PRN', models.CharField(max_length=100)),
                ('User_Name', models.CharField(blank=True, max_length=100, null=True)),
                ('account', models.CharField(blank=True, max_length=100, null=True)),
                ('User_Date', models.DateTimeField(blank=True, null=True)),
                ('Dept', models.CharField(blank=True, max_length=100, null=True)),
                ('Eq_Name', models.CharField(blank=True, max_length=100, null=True)),
                ('Need', models.TextField(blank=True, max_length=2000, null=True)),
                ('Eq_Features', models.TextField(blank=True, max_length=2000, null=True)),
                ('User_Sign', models.ImageField(blank=True, null=True, upload_to='PR_usersign')),
                ('status', models.CharField(blank=True, max_length=100, null=True)),
                ('BME_Sign', models.ImageField(blank=True, null=True, upload_to='PR_bmesign')),
                ('BME_Comment', models.TextField(blank=True, max_length=2000, null=True)),
                ('BME_Date', models.DateTimeField(blank=True, null=True)),
                ('Admin_Sign', models.ImageField(blank=True, null=True, upload_to='PR_adminsign')),
                ('Admin_Comment', models.TextField(blank=True, max_length=2000, null=True)),
                ('Admin_Date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Workbook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wo_id', models.CharField(max_length=100)),
                ('asset_id', models.CharField(max_length=100)),
                ('asset_name', models.CharField(blank=True, max_length=100, null=True)),
                ('asset_type', models.CharField(blank=True, choices=[('CRITICAL', 'CRITICAL'), ('NON-CRITICAL', 'NON-CRITICAL'), ('MISCELLANEOUS', 'MISCELLANEOUS')], max_length=100, null=True)),
                ('description', models.TextField(max_length=2000)),
                ('parts_description', models.TextField(blank=True, max_length=2000, null=True)),
                ('parts_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('make', models.CharField(blank=True, max_length=100, null=True)),
                ('model', models.CharField(blank=True, max_length=100, null=True)),
                ('dept', models.CharField(blank=True, max_length=100, null=True)),
                ('reportingDept', models.CharField(blank=True, max_length=100, null=True)),
                ('slno', models.CharField(blank=True, max_length=100, null=True)),
                ('wotype', models.CharField(blank=True, max_length=100, null=True)),
                ('action', models.TextField(blank=True, max_length=2000, null=True)),
                ('wo_date', models.DateTimeField(blank=True, null=True)),
                ('wo_attended', models.DateTimeField(blank=True, null=True)),
                ('wo_done', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(blank=True, max_length=100, null=True)),
                ('reporter', models.CharField(blank=True, max_length=100, null=True)),
                ('loginid', models.CharField(blank=True, max_length=100, null=True)),
                ('eng_id', models.CharField(blank=True, max_length=100, null=True)),
                ('woapprover', models.CharField(blank=True, max_length=100, null=True)),
                ('usersign', models.ImageField(blank=True, null=True, upload_to='Wo_usersign/')),
                ('eng_sign', models.ImageField(blank=True, null=True, upload_to='Wo_engsign/')),
                ('SR_report', models.FileField(blank=True, null=True, upload_to='Service_report/')),
                ('invoice', models.FileField(blank=True, null=True, upload_to='Wo_invoice/')),
                ('rsndtime', models.IntegerField(blank=True, null=True)),
                ('downtime', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='InstallationDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(null=True, upload_to='Installation_doc/')),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Installation_Doc', to='BMEAPP.asset')),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(null=True, upload_to='Purchase_doc/')),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Purchase_Doc', to='BMEAPP.asset')),
            ],
        ),
        migrations.CreateModel(
            name='TrainigDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(null=True, upload_to='TrainigDocument/')),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Trainig_Document', to='BMEAPP.asset')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fcm_token', models.CharField(blank=True, max_length=255, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WorkDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_id', models.CharField(max_length=100)),
                ('document', models.FileField(blank=True, null=True, upload_to='Work_doc/')),
                ('workbook', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_documents', to='BMEAPP.workbook')),
            ],
        ),
    ]
