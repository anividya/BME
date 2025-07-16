from .models import Workbook, Asset
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q

def get_wopass_data(user_group, assets, userdept):
    sidebar_map = {
        'BMEADMIN': 'sidebar.html',
        'BMESTAFF': 'sidebarbmestaff.html',
        'NURSING': 'sidebarNurse.html',
        'MANAGEMENT': 'sidebarAdmin.html'
    }

    if user_group in ["BMEADMIN", "BMESTAFF", "MANAGEMENT"]:
        queryset = Workbook.objects.all()
        assetqueryset = Asset.objects.all()
    else:
        queryset = Workbook.objects.filter(reportingDept=userdept)
        assetqueryset = Asset.objects.filter(dept=userdept)

    thirty_days_ago = timezone.now() - timedelta(days=30)
    status_counts = {
        'CLOSED': queryset.filter(status='CLOSED', wo_done__gte=thirty_days_ago).count(),
        'WATUSRAPR': queryset.filter(status='WATUSRAPR').count(),
        'ASSIGNED': queryset.filter(status='ASSIGNED').count(),
        'RELEASED': queryset.filter(status='RELEASED').count(),
        'PPM_DUE': assetqueryset.filter(pmstat='OVER DUE').count(),
        'CAL_DUE': assetqueryset.filter(calstat='OVER DUE', assetid__startswith='CH').count()
    }

    sidebar_template = sidebar_map.get(user_group)

    group_data = {
        'BMEADMIN': {'sidebar_template': sidebar_template, 'hovered2': "hovered"},
        'BMESTAFF': {'sidebar_template': sidebar_template, 'hovered2': "hovered", 'assets': assets},
        'NURSING': {'sidebar_template': sidebar_template, 'hovered2': "hovered", 'assets': assets},
        'MANAGEMENT': {'sidebar_template': sidebar_template, 'hovered2': "hovered", 'assets': assets},
    }

    result = group_data.get(user_group, {'sidebar_template': 'sidebar.html'})
    result['status_counts'] = status_counts
    return result
