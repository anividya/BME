# BMEAPP/tasks.py
from celery import shared_task
from datetime import datetime, date
import logging
from .models import Asset
from django.db.models import Q
from .ppm_cal_WO import add_pmwo

logger = logging.getLogger(__name__)

@shared_task
def print_hai():
    logger.info(f"Hai - Task ran at {datetime.now()}")
    return "Hai printed"

@shared_task
def PPMGeneration():
    runstatus = update_pm_cal_status()
    today = date.today()
    today_month = today.strftime('%b').upper()         # e.g., 'JUN'
    today_year = today.year                            # e.g., 2025
    todayMY = f"{today_month}{today_year}"             # e.g., 'JUN2025'

    created_count = 0

    # Filter relevant assets
    assetlist = Asset.objects.filter(pmstat='OVER DUE')
    calassetlist = Asset.objects.filter(calstat='OVER DUE')
    logger.info(f"{assetlist.count()} assets found for PPM check.")
    logger.info(f"{calassetlist.count()} assets found for CAL check.")

    def get_month_list(month_str):
        if not month_str:
            return []
        return [m.strip().upper() for m in month_str.split(',') if m.strip()]
    #--------PPM GENERATION-------------
    for asset in assetlist:
        ppm_months = get_month_list(asset.pmmonth)
        logger.info(f"Checking asset {asset.assetid} (LPMG: {asset.LPMG}) for month: {today_month}")

        if today_month in ppm_months:
            if asset.LPMG is None or asset.LPMG.strip().upper() != todayMY:
                id = asset.assetid
                wotype = 'PPM'
                result = add_pmwo(id,wotype)
                asset.LPMG = todayMY
                asset.save()
                logger.info(f"PPM WO created for asset {asset.assetid}:{result}")
                created_count += 1
            else:
                logger.info(f"Asset {asset.assetid} already has LPMG as {todayMY}, skipping.")
        else:
            logger.info(f"Current month {today_month} not in PPM months for asset {asset.assetid}, skipping.")

        #--------CAL GENERATION-------------
    for asset in calassetlist:
        cal_months = get_month_list(asset.calmonth)
        logger.info(f"Checking asset {asset.assetid} (LPMG: {asset.LCALG}) for month: {today_month}")

        if today_month in cal_months:
            if asset.LPMG is None or asset.LPMG.strip().upper() != todayMY:
                id = asset.assetid
                wotype = 'CAL'
                result = add_pmwo(id,wotype)
                asset.LCALG = todayMY
                asset.save()
                logger.info(f"CAL WO created for asset {asset.assetid}:")
                created_count += 1
            else:
                logger.info(f"Asset {asset.assetid} already has LCALG as {todayMY}, skipping.")
        else:
            logger.info(f"Current month {today_month} not in CAL months for asset {asset.assetid}, skipping.")


def update_pm_cal_status():
    today = datetime.today()
    current_year = today.year
    current_month = today.month

    try:
        def process_assets(assets, due_field, status_field, updates_list):
            for asset in assets:
                due_date = getattr(asset, due_field)

                if (due_date.year < current_year) or \
                   (due_date.year == current_year and due_date.month <= current_month):
                    setattr(asset, status_field, 'OVER DUE')
                    logger.info(f"[{status_field}] Asset: {asset.assetid}, Due: {due_date} -> OVER DUE")
                else:
                    setattr(asset, status_field, 'NOT DUE')
                    logger.info(f"[{status_field}] Asset: {asset.assetid}, Due: {due_date} -> NOT DUE")

                updates_list.append(asset)

        # --- PM Check ---
        pm_assets = Asset.objects.exclude(pmdue__isnull=True)
        pm_updates = []
        process_assets(pm_assets, 'pmdue', 'pmstat', pm_updates)

        # --- CAL Check ---
        cal_assets = Asset.objects.exclude(caldue__isnull=True)
        cal_updates = []
        process_assets(cal_assets, 'caldue', 'calstat', cal_updates)

        # --- Bulk Updates ---
        if pm_updates:
            Asset.objects.bulk_update(pm_updates, ['pmstat'])
        if cal_updates:
            Asset.objects.bulk_update(cal_updates, ['calstat'])

        logger.info(f"PM/CAL update complete. PM: {len(pm_updates)}, CAL: {len(cal_updates)}")
        
    except Exception as e:
        logger.error(f"Error in update_pm_cal_status: {e}")

