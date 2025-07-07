# BMEAPP/tasks.py
from celery import shared_task
from datetime import datetime, date
import logging
from BMEAPP.models import Asset
from django.db.models import Q
from BMEAPP.ppm_cal_WO import add_pmwo

logger = logging.getLogger(__name__)

def PPMGeneration():
    today = date.today()
    ppmWOSTAT = None  # Declare it with default value
    # Update pmstat for all assets due this month
    Asset.objects.filter(pmdue__month=today.month, pmdue__year=today.year).update(pmstat="OVER DUE")

    # Get ME assets with pmstat as "OVER DUE"
    assetlist = Asset.objects.filter(pmstat="OVER DUE", assetid__startswith="CH")

    # Format current date as 'MON YYYY' (e.g., 'MAY 2025')
    result = today.strftime('%b').upper() + f'{today.year}'

    for item in assetlist:
        if item.LPMG != result:
            #id = item.assetid
            #ppmWOSTAT = add_pmwo(id)
            #item.LPMG = result
            #item.save()
            print("crated")