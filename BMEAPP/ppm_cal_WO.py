from .models import Asset, Workbook
from .forms import Create_WorkForm
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def add_pmwo(asset_id, wotype):
    # Validate wotype
    if wotype not in ('PPM', 'CAL'):
        msg = f"Invalid or missing WO type for asset {asset_id}"
        logger.error(msg)
        return msg

    description = 'Preventive Maintenance Due' if wotype == 'PPM' else 'Calibration Due'

    try:
        asset = Asset.objects.get(assetid=asset_id)
    except Asset.DoesNotExist:
        msg = f"Asset {asset_id} not found"
        logger.error(msg)
        return msg

    # Generate new WO ID
    try:
        last_pk = Workbook.objects.latest('pk').pk
    except Workbook.DoesNotExist:
        last_pk = 0
    woid = f"WO-{last_pk + 1}"

    form_data = {
        'wo_id': woid,
        'asset_id': asset.assetid,
        'asset_name': asset.assetname,
        'description': description,
        'make': asset.asset_make,
        'model': asset.asset_model,
        'dept': asset.dept,
        'slno': asset.slno,
        'wo_date': datetime.now(),
        'status': 'RELEASED',
        'reporter': 'SYS',
        'loginid': 'SYS',
        'usersign': None,
    }

    work_form = Create_WorkForm(data=form_data)

    if work_form.is_valid():
        work = work_form.save(commit=False)
        work.wotype = wotype
        work.save()
        logger.info(f"{wotype} Work Order {woid} created for asset {asset_id}")
        return "Work order created successfully"
    else:
        logger.error(f"Form error for asset {asset_id}: {work_form.errors}")
        return f"Form Error: {work_form.errors}"
    
def add_pmwoonly(asset_id, wotype):
    # Validate wotype
    if wotype not in ('PPM'):
        msg = f"Error"
        return msg

    description = 'Preventive Maintenance Due'

    try:
        asset = Asset.objects.get(assetid=asset_id)
    except Asset.DoesNotExist:
        msg = f"Error"
        return msg

    # Generate new WO ID
    try:
        last_pk = Workbook.objects.latest('pk').pk
    except Workbook.DoesNotExist:
        last_pk = 0
    woid = f"WO-{last_pk + 1}"

    form_data = {
        'wo_id': woid,
        'asset_id': asset.assetid,
        'asset_name': asset.assetname,
        'description': description,
        'make': asset.asset_make,
        'model': asset.asset_model,
        'dept': asset.dept,
        'slno': asset.slno,
        'wo_date': datetime.now(),
        'status': 'RELEASED',
        'reporter': 'SYS',
        'loginid': 'SYS',
        'usersign': None,
    }

    work_form = Create_WorkForm(data=form_data)

    if work_form.is_valid():
        work = work_form.save(commit=False)
        work.wotype = wotype
        work.save()
        return "Success"
    else:
        return f"Error"

def add_calwoonly(asset_id, wotype):
    # Validate wotype
    if wotype not in ('CAL'):
        msg = f"Error"
        return msg

    description = 'Calibration Due'

    try:
        asset = Asset.objects.get(assetid=asset_id)
    except Asset.DoesNotExist:
        msg = f"Error"
        return msg

    # Generate new WO ID
    try:
        last_pk = Workbook.objects.latest('pk').pk
    except Workbook.DoesNotExist:
        last_pk = 0
    woid = f"WO-{last_pk + 1}"

    form_data = {
        'wo_id': woid,
        'asset_id': asset.assetid,
        'asset_name': asset.assetname,
        'description': description,
        'make': asset.asset_make,
        'model': asset.asset_model,
        'dept': asset.dept,
        'slno': asset.slno,
        'wo_date': datetime.now(),
        'status': 'RELEASED',
        'reporter': 'SYS',
        'loginid': 'SYS',
        'usersign': None,
    }

    work_form = Create_WorkForm(data=form_data)

    if work_form.is_valid():
        work = work_form.save(commit=False)
        work.wotype = wotype
        work.save()
        return "Success"
    else:
        return f"Error"