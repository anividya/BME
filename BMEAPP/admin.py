from django.contrib import admin
# REMOVE this code if present in admin.py
from django_celery_beat.models import (
    PeriodicTask, IntervalSchedule, CrontabSchedule, SolarSchedule, ClockedSchedule
)

#admin.site.register(PeriodicTask)
#admin.site.register(IntervalSchedule)
#admin.site.register(CrontabSchedule)
#admin.site.register(SolarSchedule)
#admin.site.register(ClockedSchedule)
from .models import Departments  # Import the model

@admin.register(Departments)
class DepartmentsAdmin(admin.ModelAdmin):
    list_display = ('LCNID', 'LOCATION', 'PARENT_DEPT')  # Columns to show in admin table
    search_fields = ('LCNID', 'LOCATION')  # Optional: adds a search bar

# Alternatively, you can register like this:
# admin.site.register(Departments, DepartmentsAdmin)
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from fcm_django.models import FCMDevice

User = get_user_model()

@admin.action(description='Send "You selected" notification')
def send_you_selected(modeladmin, request, queryset):
    for user in queryset:
        FCMDevice.objects.filter(user=user).send_message(title="Alert", body="You selected")

# ✅ Only register User if not already registered
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    actions = [send_you_selected]
