from django.db import models
from datetime import datetime, date
from django.db.models.fields import CharField
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

def validate_numeric(value):
    if not value.isnumeric():
        raise ValidationError('Input must be a number')

choice = (
    ('ACTIVE','ACTIVE'),
    ('CONDEM','CONDEM'),
    ('RETURNED','RETURNED'),
    ('RENTAL','RENTAL'),
)


# declare a new model with a name "GeeksModel"
class Asset(models.Model):
    assetid = CharField(max_length=100)
    assetname = CharField(max_length=100)
    asset_make = CharField(max_length=100)
    asset_model = CharField(max_length=100)
    slno = CharField(max_length=100)
    dept = CharField(max_length=100)
    pmdone = models.DateField(auto_now_add=False, auto_now=False, blank=True)
    pmdur = models.IntegerField(null=True)
    pmdue = models.DateField(auto_now_add=False, auto_now=False, blank=True)
    pmstat = CharField(max_length=100,null=True)
    caldue = models.DateField(auto_now_add=False, auto_now=False, blank=True)
    caldur = models.IntegerField(null=True)
    caldone = models.DateField(auto_now_add=False, auto_now=False, blank=True)
    calstat = CharField(max_length=100,null=True)
    wrstart = models.DateField(auto_now_add=False, auto_now=False, blank=True)
    wrend = models.DateField(auto_now_add=False, auto_now=False, blank=True)
    warranty = CharField(max_length=100,null=True)
    mcstart = models.DateField(auto_now_add=False, auto_now=False, blank=True)
    mcend = models.DateField(auto_now_add=False, auto_now=False, blank=True)
    amc_cmc = CharField(max_length=100,null=True)
    stat = CharField(max_length=100,choices=choice)
    doc = models.FileField(upload_to='Asset_doc',null=True)
    invoice = models.FileField(upload_to='Asset_invoice',null=True)
    
    def save(self,*arg,**kwargs):
        if self.pmdue>date.today():
            self.pmstat = "NOT DUE"
        else:
            self.pmstat = "OVER DUE"  
        super(Asset,self).save(*arg,**kwargs)

class Workbook(models.Model):
    wo_id = CharField(max_length=100)
    asset_id = CharField(max_length=100)
    asset_name = CharField(max_length=100,blank=True,null=True)
    description = models.TextField(max_length=2000)
    make = CharField(max_length=100,blank=True,null=True)
    model = CharField(max_length=100,blank=True,null=True)
    dept = CharField(max_length=100,blank=True,null=True)
    slno = CharField(max_length=100,blank=True,null=True)
    action = models.TextField(max_length=2000,blank=True,null=True)
    wo_date = models.DateTimeField(auto_now_add=False, auto_now=False,blank=True,null=True)
    wo_attended = models.DateTimeField(auto_now_add=False, auto_now=False,blank=True,null=True)
    wo_done = models.DateTimeField(auto_now_add=False, auto_now=False,blank=True,null=True)
    status = CharField(max_length=100,blank=True,null=True)
    reporter = CharField(max_length=100,blank=True,null=True)
    eng_id = CharField(max_length=100,blank=True,null=True)
    sign = models.ImageField(upload_to='Wo_usersign',blank=True,null=True)
    eng_sign = models.ImageField(upload_to='Wo_engsign',blank=True,null=True)
    SR_report = models.FileField(upload_to='Service_report',blank=True,null=True)
    invoice = models.FileField(upload_to='Wo_invoice',blank=True,null=True)
    rsndtime = models.IntegerField(blank=True,null=True)
    downtime = models.IntegerField(blank=True,null=True)

    def save(self,*arg,**kwargs):
        super(Workbook,self).save(*arg,**kwargs)
