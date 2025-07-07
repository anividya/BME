from django.db import models
from datetime import datetime, date
from django.db.models.fields import CharField
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from .monthFinder import monthfind

def validate_numeric(value):
    if not value.isnumeric():
        raise ValidationError('Input must be a number')

choice = (
    ('ACTIVE','ACTIVE'),
    ('CONDEM','CONDEM'),
    ('RETURNED','RETURNED'),
    ('RENTAL','RENTAL'),
)

assettype = (
    ('CRITICAL','CRITICAL'),
    ('NON-CRITICAL','NON-CRITICAL'),
    ('MISCELLANEOUS','MISCELLANEOUS'),
)


# declare a new model with a name "GeeksModel"
class Asset(models.Model):
    assetid = CharField(max_length=100,db_index=True,unique=True)
    assetname = CharField(max_length=100,blank=True,null=True,db_index=True)
    asset_make = CharField(max_length=100,blank=True,null=True,db_index=True)
    asset_model = CharField(max_length=100,blank=True,null=True,db_index=True)
    slno = CharField(max_length=100,blank=True,null=True,db_index=True)
    dept = CharField(max_length=100,blank=True,null=True,db_index=True)
    supplier = CharField(max_length=100,blank=True,null=True,db_index=True)
    insdate = models.DateField(auto_now_add=False, auto_now=False, blank=True,null=True,db_index=True)
    pmdone = models.DateField(auto_now_add=False, auto_now=False, blank=True,null=True,db_index=True)
    pmdur = models.IntegerField(blank=True,null=True,db_index=True)
    pmdue = models.DateField(auto_now_add=False, auto_now=False, blank=True,null=True,db_index=True)
    pmmonth = CharField(max_length=100,blank=True, null=True,db_index=True)
    LPMG = CharField(max_length=100,blank=True,null=True,db_index=True)
    pmstat = CharField(max_length=100,blank=True,null=True,db_index=True)
    caldue = models.DateField(auto_now_add=False, auto_now=False, blank=True,null=True,db_index=True)
    caldur = models.IntegerField(blank=True,null=True,db_index=True)
    caldone = models.DateField(auto_now_add=False, auto_now=False, blank=True,null=True,db_index=True)
    calvendor = CharField(max_length=100,blank=True,null=True,db_index=True)
    calmonth = CharField(max_length=100,blank=True, null=True,db_index=True)
    LCALG = CharField(max_length=100,blank=True,null=True,db_index=True)
    calstat = CharField(max_length=100,blank=True,null=True,db_index=True)
    wrstart = models.DateField(auto_now_add=False, auto_now=False, blank=True,null=True,db_index=True)
    wrend = models.DateField(auto_now_add=False, auto_now=False, blank=True,null=True,db_index=True)
    warranty = CharField(max_length=100,blank=True,null=True,db_index=True)
    mcstart = models.DateField(auto_now_add=False, auto_now=False, blank=True,null=True,db_index=True)
    mcend = models.DateField(auto_now_add=False, auto_now=False, blank=True,null=True,db_index=True)
    amc_cmc = CharField(max_length=100,blank=True,null=True,db_index=True)
    LMCG = CharField(max_length=100,blank=True,null=True,db_index=True)
    stat = CharField(max_length=100,choices=choice,blank=True,null=True,db_index=True)
    asset_type = CharField(max_length=100,choices=assettype,blank=True,null=True,db_index=True)
    
    def save(self,*arg,**kwargs):
        super(Asset,self).save(*arg,**kwargs)

class InstallationDocument(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='Installation_Doc')
    document = models.FileField(upload_to='Installation_doc/',null=True)

    def __str__(self):
        return f'{self.asset.assetid} - {self.document.name}'

class PurchaseDocument(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='Purchase_Doc')
    document = models.FileField(upload_to='Purchase_doc/',null=True)

    def __str__(self):
        return f'{self.asset.assetid} - {self.document.name}'

class TrainigDocument(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='Trainig_Document')
    document = models.FileField(upload_to='TrainigDocument/',null=True)

    def __str__(self):
        return f'{self.asset.assetid} - {self.document.name}'

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
import firebase_admin
from firebase_admin import credentials, messaging
import os
import json


class Workbook(models.Model):
    wo_id = models.CharField(max_length=100)
    asset_id = models.CharField(max_length=100)
    asset_name = models.CharField(max_length=100, blank=True, null=True)
    asset_type = models.CharField(max_length=100, choices=assettype, blank=True, null=True)
    description = models.TextField(max_length=2000)
    parts_description = models.TextField(max_length=2000, blank=True, null=True)
    parts_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    make = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    dept = models.CharField(max_length=100, blank=True, null=True)
    reportingDept = models.CharField(max_length=100, blank=True, null=True)
    slno = models.CharField(max_length=100, blank=True, null=True)
    wotype = models.CharField(max_length=100, blank=True, null=True)
    action = models.TextField(max_length=2000, blank=True, null=True)
    wo_date = models.DateTimeField(auto_now_add=False, auto_now=False, blank=True, null=True)
    wo_attended = models.DateTimeField(auto_now_add=False, auto_now=False, blank=True, null=True)
    wo_done = models.DateTimeField(auto_now_add=False, auto_now=False, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    reporter = models.CharField(max_length=100, blank=True, null=True)
    loginid = models.CharField(max_length=100, blank=True, null=True)
    eng_id = models.CharField(max_length=100, blank=True, null=True)
    woapprover = models.CharField(max_length=100, blank=True, null=True)
    usersign = models.ImageField(upload_to='Wo_usersign/', blank=True, null=True)
    eng_sign = models.ImageField(upload_to='Wo_engsign/', blank=True, null=True)
    SR_report = models.FileField(upload_to='Service_report/', blank=True, null=True)
    invoice = models.FileField(upload_to='Wo_invoice/', blank=True, null=True)
    rsndtime = models.IntegerField(blank=True, null=True)
    downtime = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return self.wo_id
    
    def save(self, *args, **kwargs):
        # Add any pre-save logic here if needed
        super().save(*args, **kwargs)


class WorkDocument(models.Model):
    workbook = models.ForeignKey(Workbook, on_delete=models.CASCADE, related_name='work_documents')
    asset_id = models.CharField(max_length=100)
    document = models.FileField(upload_to='Work_doc/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.workbook.wo_id} - {self.document.name}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fcm_token = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.user.username

from .firebase_service import FirebaseService

def send_notification(user, wo_id):
    try:
        profile = UserProfile.objects.get(user__username=user)
        if profile.fcm_token:
            FirebaseService.send_notification(
                token=profile.fcm_token,
                title='New Work Assignment',
                body=f'You have been assigned work order: {wo_id}'
            )
            return True
    except Exception as e:
        print(f"Notification error: {e}")
    return False

@receiver(pre_save, sender=Workbook)
def workbook_pre_save(sender, instance, **kwargs):
    """Signal to send notification when eng_id is changed"""
    try:
        if instance.pk:  # Only for existing instances
            old_instance = Workbook.objects.get(pk=instance.pk)
            if old_instance.eng_id != instance.eng_id and instance.eng_id:
                # Eng_id has changed and is not empty
                send_notification(instance.eng_id, instance.wo_id)
    except Workbook.DoesNotExist:
        pass  # New instance, no notification needed


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create profile when new user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save profile when user is saved"""
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)

class Gatepass(models.Model):
    pass_id = CharField(max_length=100)
    asset_name = CharField(max_length=100,blank=True,null=True)
    collector_name = CharField(max_length=100,blank=True,null=True)
    contact_num = CharField(max_length=100,blank=True,null=True)
    sender_name = CharField(max_length=100,blank=True,null=True)
    send_to = CharField(max_length=100,blank=True,null=True)
    uoq = CharField(max_length=100,blank=True,null=True)
    asset = CharField(max_length=100,blank=True,null=True)
    serial = CharField(max_length=100,blank=True,null=True)
    gatepasstype = CharField(max_length=100,blank=True,null=True)
    qty = models.IntegerField(blank=True,null=True)
    description = models.TextField(max_length=2000)
    request_date = models.DateTimeField(auto_now_add=False, auto_now=False,blank=True,null=True)
    out_date = models.DateTimeField(auto_now_add=False, auto_now=False,blank=True,null=True)
    in_date = models.DateTimeField(auto_now_add=False, auto_now=False,blank=True,null=True)
    collector_sign = models.ImageField(upload_to='gpcollectorsign',blank=True,null=True)
    bme_sign = models.ImageField(upload_to='gpbmesign',blank=True,null=True)
    admin_sign = models.ImageField(upload_to='gpadminsign',blank=True,null=True)
    status = CharField(max_length=100,blank=True,null=True)

    def save(self,*arg,**kwargs):
        super(Gatepass,self).save(*arg,**kwargs)
    
class PRR(models.Model):
    PRN = CharField(max_length=100)
    User_Name = CharField(max_length=100,blank=True,null=True)
    account = CharField(max_length=100,blank=True,null=True)
    User_Date = models.DateTimeField(auto_now_add=False, auto_now=False,blank=True,null=True)
    Dept = CharField(max_length=100,blank=True,null=True)
    Eq_Name = CharField(max_length=100,blank=True,null=True)
    Need = models.TextField(max_length=2000,blank=True,null=True)
    Eq_Features = models.TextField(max_length=2000,blank=True,null=True)
    User_Sign = models.ImageField(upload_to='PR_usersign',blank=True,null=True)
    status = CharField(max_length=100,blank=True,null=True)
    BME_Sign = models.ImageField(upload_to='PR_bmesign',blank=True,null=True)
    BME_Comment = models.TextField(max_length=2000,blank=True,null=True)
    BME_Date = models.DateTimeField(auto_now_add=False, auto_now=False,blank=True,null=True)
    Admin_Sign = models.ImageField(upload_to='PR_adminsign',blank=True,null=True)
    Admin_Comment = models.TextField(max_length=2000,blank=True,null=True)
    Admin_Date = models.DateTimeField(auto_now_add=False, auto_now=False,blank=True,null=True)

    def save(self,*arg,**kwargs):
        super(PRR,self).save(*arg,**kwargs)

class Departments(models.Model):
    LCNID = CharField(max_length=100)
    LOCATION = CharField(max_length=100)
    PARENT_DEPT = CharField(max_length=100,blank=True,null=True)

    def save(self,*arg,**kwargs):
        super(Departments,self).save(*arg,**kwargs)
