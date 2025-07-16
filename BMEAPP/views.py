# ========================
# Python Standard Library
# ========================
import os
import re
import json
import base64
import logging
from datetime import datetime, timedelta, time, date
from collections import defaultdict
from tempfile import NamedTemporaryFile

# ========================
# Third-Party Libraries
# ========================
import requests
import pdfkit
import pythoncom
import docx2pdf
from dateutil.relativedelta import relativedelta
from openpyxl import Workbook
from comtypes import CoInitialize, CoUninitialize
from docx import Document
from docx.shared import Inches
from win32com.client import Dispatch

# ========================
# Django Core Imports
# ========================
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from django.http import (
    HttpResponse, JsonResponse, FileResponse,
    HttpResponseRedirect,Http404
)
from django.shortcuts import (
    render, redirect, get_object_or_404
)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth import (
    authenticate, login, logout,
    get_user_model
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User, Group
from django.core.files.base import ContentFile
from django.core.paginator import Paginator, EmptyPage
from django.core.exceptions import ValidationError
from django.db import transaction, DatabaseError
from django.db.models import (
    Q, Min, Max, IntegerField
)
from django.db.models.functions import (
    Substr, Length, Cast
)
from django.forms import (
    formset_factory, modelformset_factory
)
from django.template.loader import render_to_string

# ========================
# Django REST Framework
# ========================
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

# ========================
# Local App Imports
# ========================
from .models import (
    Workbook, Gatepass, PRR, Asset,
    InstallationDocument, TrainigDocument,
    PurchaseDocument, WorkDocument, Departments
)
from .forms import (
    WorkbookForm, WorkDocumentFormSet,
    GatepassForm, Create_AssetForm,
    Create_WorkForm, prCreateform,
    UserRegistrationForm, ReportFilterForm,
    GatepassApproval, gtSend, DepartmentForm
)
from .decorators import allowed_users
from .serializers import WorkbookSerializer, GatepassSerializer
from .wopass_function import get_wopass_data
from .viewwo_passFunction import (
    get_woviewpass_data, woUserapprovepass_data
)
from .myWork_passFunction import get_myWorkpass_data
from .gatePass_passFunction import get_gatepass_data
from .prPassData import pr_pass_data
from .praprvpassdata import pr_apr_pass
from .assetViewPassData import getAssetpassData
from .monthFinder import monthfind
from .tst import next_ppmMonth, next_ppmMonthview
from .ppm_cal_WO import add_calwoonly, add_pmwoonly, add_pmwo

# ========================
# Firebase Notifications
# ========================
from fcm_django.models import FCMDevice


# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
woper = {'MANAGEMENT', 'NURSING', 'OR'}
bmeteam = {'BMEADMIN', 'BMESTAFF'}
gtapprove = {'BMEADMIN', 'MANAGEMENT'}
prapprove = {'BMEADMIN', 'MANAGEMENT'}
prcreate = {'MANAGEMENT', 'NURSING', 'OR', 'BMEADMIN'}
viewSr = {'BMEADMIN', 'BMESTAFF', 'MANAGEMENT', 'NURSING', 'OR', 'BMEADMIN'}
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////


def loginpage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return render(request, 'index.html')

        else:
            messages.error(request, 'Username or Password incorrect')
            return render(request, 'login.html')

    else:
        return render(request, "login.html")
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

def logoutuser(request):
    logout(request)
    return redirect('login/?next=/')
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////


def check_username(request):
    username = request.GET.get('username', None)
    exists = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({'exists': exists})
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
@allowed_users('BMEADMIN')
def register(request):
    depts = Departments.objects.all()
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user_data = form.cleaned_data

            # Pure function: create_user_data, returns a user object with hashed password
            def create_user_data(data):
                return {
                    'username': data['username'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    # Hash the password
                    'password': make_password(data['password']),
                }

            # Use the immutable data returned from `create_user_data`
            new_user_data = create_user_data(user_data)

            # Check if the username already exists
            if User.objects.filter(username=new_user_data['username']).exists():
                form.add_error(
                    'username', 'This username is already taken. Please choose another one.')
            else:
                # Create the user object but do not save it yet
                user = User(**new_user_data)  # Unpack the new_user_data dict
                user.save()  # Save the user

                # Group is immutable, so assign the group using its ID
                group = Group.objects.get(
                    id=user_data['group'].id)  # Get group by its ID
                user.groups.add(group)  # Add user to the group

                # Redirect to login page
                return render(request, 'utilities.html',{'sidebar_template': "sidebar.html", 'hovered11': "hovered"})

    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form,'depts': depts,'sidebar_template': "sidebar.html",'hovered11': "hovered"})

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
def index(request):
    assetcat = request.GET.get('asset_type')
    if assetcat:
        assetcatogery = request.GET.get('asset_type')
    else:
        assetcatogery = "CH"

    user_group = None
    #================================================================================
    for group in request.user.groups.all():
        user_group = group.name
    userdept = request.user.last_name
    thirty_days_ago = timezone.now() - timedelta(days=30)
    if user_group in ["BMEADMIN", "BMESTAFF", "MANAGEMENT"]:
        queryset = Workbook.objects.all()
        assetqueryset = Asset.objects.all()
    else:
        queryset = Workbook.objects.filter(reportingDept=userdept)
        assetqueryset = Asset.objects.filter(dept=userdept)

    status_counts = {
        'CLOSED': queryset.filter(status='CLOSED', wo_done__gte=thirty_days_ago).count(),
        'WATUSRAPR': queryset.filter(status='WATUSRAPR').count(),
        'ASSIGNED': queryset.filter(status='ASSIGNED').count(),
        'RELEASED': queryset.filter(status='RELEASED').count(),
        'PPM_DUE': assetqueryset.filter(pmstat='OVER DUE').count(),
        'CAL_DUE': assetqueryset.filter(calstat='OVER DUE', assetid__startswith='CH').count(),
    }
    #================================================================================
    ppmduenum = Asset.objects.filter(
        Q(pmstat='OVER DUE') & Q(assetid__startswith='CH')).count()

    sidebar_map = {'BMEADMIN': 'sidebar.html', 'BMESTAFF': 'sidebarbmestaff.html',
                   'NURSING': 'sidebarNurse.html', 'MANAGEMENT': 'sidebarAdmin.html'}
    sidebar_template = sidebar_map.get(user_group)
    
    site_map = {'BMEADMIN': 'asset_list.html', 'BMESTAFF': 'asset_list.html',
                'NURSING': 'add_wo.html', 'MANAGEMENT': 'asset_list.html'}
    gotosite = site_map.get(user_group)

    group_data = {
        'BMEADMIN': {'sidebar_template': sidebar_template, 'hovered1': "hovered", 'status_counts': status_counts, 'assetcat': assetcatogery},
        'BMESTAFF': {'sidebar_template': sidebar_template, 'hovered1': "hovered", 'status_counts': status_counts},
        'NURSING': {'sidebar_template': sidebar_template, 'hovered2': "hovered",'status_counts': status_counts},
        'MANAGEMENT': {'sidebar_template': sidebar_template, 'hovered1': "hovered", 'status_counts': status_counts}
    }

    pass_data = group_data.get(user_group)
    pass_data['user_group'] = user_group
    return render(request, gotosite, pass_data)

    # return render(request, pass_data, 'asset_list.html')


def extract_numeric(assetid):
    """Extracts numeric part from 'CH5034A' as integer 5034"""
    match = re.match(r'^CH(\d+)', assetid)
    return int(match.group(1)) if match else 0


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
def asset_data(request):
    assetcat = request.GET.get('assettype')
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    sort_column = request.GET.get('sort_column', 'assetid')
    sort_direction = request.GET.get('sort_direction', 'asc')
    search_terms = json.loads(request.GET.get('search_terms', '[]'))

    allowed_columns = {
        'assetid', 'assetname', 'asset_make', 'asset_model',
        'slno', 'dept', 'pmstat', 'calstat'
    }
    if sort_column not in allowed_columns:
        sort_column = 'assetid'

    if assetcat=='MISSL':
        queryset = Asset.objects.filter(assetid__startswith=assetcat)
    else:
        queryset = Asset.objects.exclude(Q(assetid__iexact='nan') | Q(assetid__isnull=True))
        queryset = queryset.filter(assetid__startswith='CH')

    # Apply column-specific searches
    for i, term in enumerate(search_terms):
        if term:
            field_map = {
                0: 'assetid',
                1: 'assetname',
                2: 'asset_make',
                3: 'asset_model',
                4: 'slno',
                5: 'dept',
                6: 'pmstat',
                7: 'calstat'
            }
            if i in field_map:
                field = field_map[i]
                queryset = queryset.filter(**{f'{field}__icontains': term})

    records_total = Asset.objects.count()
    records_filtered = queryset.count()    
    assets = list(queryset)

    if sort_column == 'assetid':
        # Sort in Python using numeric part of assetid
        assets.sort(
            key=lambda x: extract_numeric(x.assetid),
            reverse=(sort_direction == 'desc')
        )
    else:
        # Use default ORM ordering for other columns
        order_by = sort_column
        if sort_direction == 'desc':
            order_by = '-' + order_by
        assets = list(queryset.order_by(order_by))

    paginator = Paginator(assets, length)
    page_number = (start // length) + 1
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        page = paginator.page(1)

    data = []
    for asset in page:
        data.append({
            'assetid': asset.assetid,
            'assetname': asset.assetname or '',
            'asset_make': asset.asset_make or '',
            'asset_model': asset.asset_model or '',
            'slno': asset.slno or '',
            'dept': asset.dept or '',
            'pmstat': asset.pmstat or '',
            'calstat': asset.calstat or '',
            'action': f'<button class="btn btn-sm btn-info view-btn" data-id="{asset.assetid}">View</button>'
        })

    return JsonResponse({
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data,
    })


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
def asset_quickview(request, asset_id):
    asset = get_object_or_404(Asset, assetid=asset_id)
    return render(request, 'asset_quickview.html', {'asset': asset})

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
@allowed_users('BMEADMIN')
def add_asset(request):
    depts = Departments.objects.all()
    if request.method == 'POST':
        asset_form = Create_AssetForm(request.POST)
        if asset_form.is_valid():
            asset = asset_form.save(commit=False)
            miss_asset = Asset.objects.filter(
                assetid__startswith='MISSL').order_by('-id').first()

            if request.POST.get('asset_type') == "MISCELLANEOUS":
                if miss_asset:
                    #last_pk = miss_asset.pk
                    #assetid = 'MISSL-CH'+str(last_pk+1)
                    last_pk = miss_asset.pk if miss_asset else 0
                    while True:
                        assetid = 'MISSL-CH' + str(last_pk + 1)
                        assetidck = 'CH' + str(last_pk + 1)
                        if not Asset.objects.filter(assetid__in=[assetid, assetidck]).exists():
                            break
                        last_pk += 1
                else:
                    last_pk = 0
                    assetid = 'MISSL-CH'+str(last_pk+1)
            else:
                if Asset.objects.exists():
                    last_pk = Asset.objects.aggregate(max_pk=Max('pk'))['max_pk'] or 0
                    while True:
                        assetid = 'MISSL-CH' + str(last_pk + 1)
                        assetidck = 'CH' + str(last_pk + 1)
                        if not Asset.objects.filter(assetid__in=[assetid, assetidck]).exists():
                            break
                        last_pk += 1

                    assetid = assetidck
                else:
                    last_pk = 0
                    assetid = 'CH'+str(last_pk+1)

            ppmDone = request.POST.get('pmdone')
            pmduaration = request.POST.get('pmdur')
            calDone = request.POST.get('caldone')
            calduaration = request.POST.get('caldur')
            pmMonths = monthfind(ppmDone, pmduaration)
            calMonths = monthfind(calDone, calduaration)

            pmdone_str = request.POST.get('pmdone')
            pmduaration_str = request.POST.get('pmdur')
            input_date = datetime.strptime(pmdone_str, "%Y-%m-%d")
            pmduaration = int(pmduaration_str)
            new_pmdate = input_date + relativedelta(months=pmduaration)

            cal_inputDate = datetime.strptime(calDone, "%Y-%m-%d")
            cal_Duaration = int(calduaration)
            new_caldate = cal_inputDate + relativedelta(months=cal_Duaration)

            
            today = date.today()

            pmstat = "OVER DUE" if new_pmdate.month == today.month and new_pmdate.year == today.year else "NOT DUE"
            calstat = "OVER DUE" if new_caldate.month == today.month and new_caldate.year == today.year else "NOT DUE"
            warranty = "NO WARRANTY" if asset.wrend.month == today.month and asset.wrend.year == today.year else "UNDER WARRANTY"
            
            asset.pmdue = new_pmdate
            asset.pmstat = pmstat
            asset.caldue = new_caldate
            asset.calstat = calstat
            asset.pmmonth = pmMonths
            asset.calmonth = calMonths
            asset.assetid = assetid
            asset.mcstart = asset.wrstart
            asset.mcend = asset.wrend
            asset.amc_cmc = "UNDER WARRANTY"
            asset.warranty = warranty

            asset.save()

            for file in request.FILES.getlist('Installation_Doc'):
                InstallationDocument.objects.create(asset=asset, document=file)

            for file in request.FILES.getlist('Trainig_Doc'):
                TrainigDocument.objects.create(asset=asset, document=file)

            for file in request.FILES.getlist('Purchase_Doc'):
                PurchaseDocument.objects.create(asset=asset, document=file)

            success = True
            asset_form = Create_AssetForm()
            sidebar_template = 'sidebar.html'
            li_class = "hovered"
            message = f"Asset {assetid} Generated successfully!"
            statuses = [
                {"id": "ACTIVE", "name": "ACTIVE"},
                {"id": "RENTAL", "name": "RENTAL"},
                {"id": "CONDEMNED", "name": "CONDEMNED"}]
            assettype = [
                {"id": "CRITICAL", "name": "CRITICAL"},
                {"id": "NON-CRITICAL", "name": "NON-CRITICAL"},
                {"id": "MISCELLANEOUS", "name": "MISCELLANEOUS"}]
            pass_data = {
                'li_class': li_class,
                'sidebar_template': sidebar_template,
                'hovered1': li_class,
                'asset_form': asset_form,
                'success': success,
                'message': message,
                'statuses': statuses,
                'assettypes': assettype,
                'depts': depts
            }
            return render(request, 'add_asset.html', pass_data)

        else:
            error = True
            asset_form = Create_AssetForm()
            sidebar_template = 'sidebar.html'
            li_class = "hovered"
            message = "Error In Saving!!"
            statuses = [
                {"id": "ACTIVE", "name": "ACTIVE"},
                {"id": "RENTAL", "name": "RENTAL"},
                {"id": "CONDEMNED", "name": "CONDEMNED"}]
            assettype = [
                {"id": "CRITICAL", "name": "CRITICAL"},
                {"id": "NON-CRITICAL", "name": "NON-CRITICAL"},
                {"id": "MISCELLANEOUS", "name": "MISCELLANEOUS"}]
            pass_data = {
                'li_class': li_class,
                'sidebar_template': sidebar_template,
                'hovered1': li_class,
                'asset_form': asset_form,
                'error': error,
                'message': message,
                'statuses': statuses,
                'assettypes': assettype,
                'depts': depts
            }
            return render(request, 'add_asset.html', pass_data)
        
    if request.method == 'GET':
        asset_form = Create_AssetForm()
        sidebar_template = 'sidebar.html'
        li_class = "hovered"
        statuses = [
            {"id": "ACTIVE", "name": "ACTIVE"},
            {"id": "RENTAL", "name": "RENTAL"},
            {"id": "CONDEMNED", "name": "CONDEMNED"}]
        assettype = [
            {"id": "CRITICAL", "name": "CRITICAL"},
            {"id": "NON-CRITICAL", "name": "NON-CRITICAL"},
            {"id": "MISCELLANEOUS", "name": "MISCELLANEOUS"}]
        pass_data = {
            'li_class': li_class,
            'sidebar_template': sidebar_template,
            'hovered1': li_class,
            'asset_form': asset_form,
            'statuses': statuses,
            'assettypes': assettype,
            'depts': depts
        }
        return render(request, 'add_asset.html', pass_data)
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
@csrf_exempt
def autocomplete_field(request):
    field = request.GET.get('field')
    term = request.GET.get('term', '')

    # Mapping allowed fields to model fields
    allowed_fields = {
        'make': 'asset_make',
        'equipment': 'assetname',
        'supplier': 'supplier',      # Ensure 'supplier' exists in your model
        'model': 'asset_model',      # Ensure 'asset_model' exists in your model
        # 'dept' : 'dept'
    }

    if field not in allowed_fields:
        return JsonResponse([], safe=False)

    db_field = allowed_fields[field]
    filter_kwargs = {f"{db_field}__icontains": term}

    matches = Asset.objects.filter(
        **filter_kwargs).values_list(db_field, flat=True).distinct()[:10]
    return JsonResponse(list(matches), safe=False)

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
@allowed_users(prapprove)
def asset_detail(request, Asset_No):
    asset_id = Asset_No
    try:
        # Get the asset by ID
        asset = Asset.objects.get(assetid=asset_id)
        works = Workbook.objects.filter(asset_id=asset_id)

        # Get the documents related to the asset
        installation_docs = InstallationDocument.objects.filter(asset=asset)
        purchase_docs = PurchaseDocument.objects.filter(asset=asset)
        training_docs = TrainigDocument.objects.filter(asset=asset)
        work_docs = WorkDocument.objects.filter(asset_id=Asset_No)

        user_group = None
        for group in request.user.groups.all():
            user_group = group.name
        template = getAssetpassData(
            user_group, asset, installation_docs, purchase_docs, training_docs, works, work_docs)
        # pass_data['message'] = "Error!!!"
        # pass_data['error'] = True
        return render(request, 'asset_detail.html', template)
    except Asset.DoesNotExist:
        # If the asset does not exist, handle it appropriately
        return render(request, 'asset_detail.html', {'error': 'Asset not found'})
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
def add_wo(request):

    assetcat = request.GET.get('asset_type')
    if assetcat:
        assetcatogery = request.GET.get('asset_type')
    else:
        assetcatogery = "CH"
    assets = Asset.objects.all()
    if request.method == 'POST':
        if request.user.is_authenticated:
            # Accessing the username of the logged-in user
            username = request.user.username
            lastname = request.user.last_name
        canvas_data = request.POST.get('canvas_data', None)
        if canvas_data:
            format, imgstr = canvas_data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            # do something with the image file
        else:
            return HttpResponse(status=505)
        signcontent = Workbook(usersign=data)
        work_form = Create_WorkForm(
            request.POST, request.FILES, instance=signcontent)
        if work_form.is_valid():
            if Workbook.objects.exists():
                last_pk = Workbook.objects.latest('pk').pk
            else:
                last_pk = 0

            try:
                assetid = request.POST.get('asset_id')
                assetiddeatails = get_object_or_404(Asset, assetid=assetid)
                asset_type = assetiddeatails.asset_type
                woid = 'WO-'+str(last_pk+1)
                work = work_form.save(commit=False)
                work.wo_id = woid
                work.loginid = username
                work.reportingDept = lastname
                work.wotype = request.POST.get('wotype')
                work.asset_type = asset_type
                work.save()
            except Http404:
                # Object not found
                return HttpResponse("Asset ID not found.", status=404)
            except DatabaseError as e:
                # Any other DB-related error
                return HttpResponse(f"Database error occurred: {str(e)}", status=500)
            except Exception as e:
                # Catch-all for any other exceptions
                return HttpResponse(f"An unexpected error occurred: {str(e)}", status=500)

            user_group = None
            for group in request.user.groups.all():
                user_group = group.name
            userdept = request.user.last_name
            pass_data = get_wopass_data(user_group, assets, userdept)
            pass_data['message'] = "Work Order Generated Succesfully!!!"
            pass_data['success'] = True
            pass_data['user_group'] = user_group
            return render(request, 'add_wo.html', pass_data)
        else:
            user_group = None
            for group in request.user.groups.all():
                user_group = group.name
            userdept = request.user.last_name
            pass_data = get_wopass_data(user_group, assets, userdept)
            pass_data['message'] = "Error!!!"
            pass_data['error'] = True
            pass_data['user_group'] = user_group
            return render(request, 'add_wo.html', pass_data)

    else:
        user_group = None
        for group in request.user.groups.all():
            user_group = group.name
        userdept = request.user.last_name
        pass_data = get_wopass_data(user_group, assets, userdept)
        pass_data['assetcat'] = assetcatogery
        pass_data['user_group'] = user_group
        return render(request, 'add_wo.html', pass_data)

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
def addwo_ajax(request, asset_id):
    assetdata = get_object_or_404(Asset, assetid=asset_id)
    if assetdata:
        asset_info = {
            'id': assetdata.assetid,
            'assetname': assetdata.assetname,
            'make': assetdata.asset_make,
            'model': assetdata.asset_model,
            'slno': assetdata.slno,
            'dept': assetdata.dept,
            'stat': "RELEASED",
            # Add any other fields you want to include
        }
    if Workbook.objects.exists():
        last_pk = Workbook.objects.latest('pk').pk
    else:
        last_pk = 0
    woid = 'WO-'+str(last_pk+1)
    now = timezone.now()
    wodata = {'key': woid,
              'date': now,
              'assetdata': asset_info
              }
    return JsonResponse(wodata)

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
def view_wo(request):
    if request.method == 'POST':
        workID = request.POST.get('wo_id')
        EngID = request.POST.get('eng_id')
        WoAttended = request.POST.get('wo_attended')
        wo_date = datetime.strptime(WoAttended, '%Y-%m-%d %H:%M')
        wo_date = timezone.make_aware(wo_date)
        # Check for required data
        if not all([workID, EngID, WoAttended]):
            worklist = Workbook.objects.all()
            user_group = None
            for group in request.user.groups.all():
                user_group = group.name

            pass_data = get_woviewpass_data(user_group, worklist)
            pass_data['user_group'] = user_group
            pass_data['datenow'] = datetime.now()
            pass_data['message'] = "Data Missing!!!"
            pass_data['error'] = True
            pass_data['PPM_DUE'] = Asset.objects.filter(
                Q(pmstat='OVER DUE') & Q(assetid__startswith='CH')).count()
            pass_data['CAL_DUE'] = Asset.objects.filter(
                Q(calstat='OVER DUE') & Q(assetid__startswith='CH')).count()
            return render(request, 'work_list.html', pass_data)

        try:
            workbook = get_object_or_404(Workbook, wo_id=workID)
        except Http404:
            # Object not found
            return HttpResponse("Workbook with given ID not found.", status=404)
        except DatabaseError as e:
            # Any other DB-related error
            return HttpResponse(f"Database error occurred: {str(e)}", status=500)
        except Exception as e:
            # Catch-all for any other exceptions
            return HttpResponse(f"An unexpected error occurred: {str(e)}", status=500)

        if workbook.status in ["ASSIGNED", "WATUSRAPR", "WTNGAPR", "WTNGCOMPANY", "WTNGPART", "CLOSED"]:
            worklist = Workbook.objects.all()
            user_group = None
            for group in request.user.groups.all():
                user_group = group.name

            pass_data = get_woviewpass_data(user_group, worklist)
            pass_data['user_group'] = user_group
            pass_data['datenow'] = datetime.now()
            pass_data['message'] = "Alredy Assinged!!!"
            pass_data['error'] = True
            pass_data['PPM_DUE'] = Asset.objects.filter(
                Q(pmstat='OVER DUE') & Q(assetid__startswith='CH')).count()
            pass_data['CAL_DUE'] = Asset.objects.filter(
                Q(calstat='OVER DUE') & Q(assetid__startswith='CH')).count()
            return render(request, 'work_list.html', pass_data)
        else:
            workbook.eng_id = EngID
            workbook.wo_attended = wo_date
            workbook.status = "ASSIGNED"
            workbook.save()

            worklist = Workbook.objects.all()
            user_group = None
            for group in request.user.groups.all():
                user_group = group.name

            pass_data = get_woviewpass_data(user_group, worklist)
            pass_data['user_group'] = user_group
            pass_data['datenow'] = datetime.now()
            pass_data['message'] = "Work Order Assinged Succesfully!!!"
            pass_data['success'] = True
            pass_data['PPM_DUE'] = Asset.objects.filter(
                Q(pmstat='OVER DUE') & Q(assetid__startswith='CH')).count()
            pass_data['CAL_DUE'] = Asset.objects.filter(
                Q(calstat='OVER DUE') & Q(assetid__startswith='CH')).count()
            return render(request, 'work_list.html', pass_data)

    else:
        worklist = Workbook.objects.all()
        user_group = None
        for group in request.user.groups.all():
            user_group = group.name

        pass_data = get_woviewpass_data(user_group, worklist)
        pass_data['user_group'] = user_group
        pass_data['datenow'] = timezone.now()
        pass_data['PPM_DUE'] = Asset.objects.filter(
            Q(pmstat='OVER DUE') & Q(assetid__startswith='CH')).count()
        pass_data['CAL_DUE'] = Asset.objects.filter(
            Q(calstat='OVER DUE') & Q(assetid__startswith='CH')).count()
        return render(request, 'work_list.html', pass_data)
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////////////////////////


def extract_numeric2(wo_id):
    """Extract the numeric part from a WO ID like 'WO-23'"""
    match = re.search(r'\d+', wo_id)
    return int(match.group()) if match else 0
# ////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
def work_data(request):
    # assetcat = request.GET.get('assettype')
    current_user = request.user
    for group in current_user.groups.all():
        user_group = group.name
    # The Last name considered as their respective department
    userdept = request.user.last_name

    if user_group in ["BMEADMIN", "BMESTAFF", "MANAGEMENT"]:
        queryset = Workbook.objects.all()
    else:
        queryset = Workbook.objects.filter(reportingDept=userdept)

    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    sort_column = request.GET.get('sort_column', 'assetid')
    sort_direction = request.GET.get('sort_direction', 'asc')
    search_terms = json.loads(request.GET.get('search_terms', '[]'))

    allowed_columns = {
        'wo_id', 'asset_id', 'asset_name', 'description',
        'wo_date', 'dept', 'status'
    }
    if sort_column not in allowed_columns:
        sort_column = 'wo_id'

    # queryset = Workbook.objects.all()

    # Apply column-specific searches
    for i, term in enumerate(search_terms):
        if term:
            field_map = {
                0: 'wo_id',
                1: 'asset_id',
                2: 'asset_name',
                3: 'description',
                4: 'wo_date',
                5: 'dept',
                6: 'status',
            }
            if i in field_map:
                field = field_map[i]
                queryset = queryset.filter(**{f'{field}__icontains': term})

    records_total = Workbook.objects.count()
    records_filtered = queryset.count()

    assets = list(queryset)

    if sort_column == 'wo_id':
        # Sort in Python using numeric part of assetid
        assets.sort(
            key=lambda x: extract_numeric2(x.wo_id),
            reverse=(sort_direction == 'desc')
        )
    else:
        # Use default ORM ordering for other columns
        order_by = sort_column
        if sort_direction == 'desc':
            order_by = '-' + order_by
        assets = list(queryset.order_by(order_by))

    paginator = Paginator(assets, length)
    page_number = (start // length) + 1
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        page = paginator.page(1)

    data = []
    for asset in page:
        data.append({
            'wo_id': asset.wo_id,
            'asset_id': asset.asset_id or '',
            'asset_name': asset.asset_name or '',
            'description': asset.description or '',
            'wo_date': asset.wo_date or '',
            'dept': asset.dept or '',
            'status': asset.status or '',
            'action': f'<button class="btn btn-sm btn-info view-btn" data-id="{asset.asset_id}">View</button>'
        })

    return JsonResponse({
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data,
    })

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
def wo_UserApproval(request):  # This is for user approval page of group work order
    rDept = request.user.last_name.strip()
    worklist = Workbook.objects.filter(
        Q(status='WATUSRAPR') &
        Q(reportingDept=rDept) &
        Q(wotype='CM'))
    user_group = None
    for group in request.user.groups.all():
        user_group = group.name

    pass_data = woUserapprovepass_data(user_group, worklist)
    pass_data['user_group'] = user_group
    pass_data['datenow'] = timezone.now()
    pass_data['PPM_DUE'] = Asset.objects.filter(
        Q(pmstat='OVER DUE') & Q(assetid__startswith='CH')).count()
    pass_data['CAL_DUE'] = Asset.objects.filter(
        Q(calstat='OVER DUE') & Q(assetid__startswith='CH')).count()
    return render(request, 'wo_userApproval.html', pass_data)
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
def wouserapprove(request):  # This is for saving the sign for group Work order
    woids = request.POST.get('selectedwo')
    eng_id = request.POST.get('eng_id')

    if not woids:
        rDept = request.user.last_name.strip()
        worklist = Workbook.objects.filter(
            Q(status='WATUSRAPR') &
            Q(reportingDept=rDept) &
            Q(wotype='CM'))

        user_group = None
        for group in request.user.groups.all():
            user_group = group.name

        pass_data = woUserapprovepass_data(user_group, worklist)
        pass_data['user_group'] = user_group
        pass_data['datenow'] = timezone.now()
        pass_data['message'] = "No work orders were selected..!!!"
        pass_data['error'] = True
        pass_data['PPM_DUE'] = Asset.objects.filter(
            Q(pmstat='OVER DUE') & Q(assetid__startswith='CH')).count()
        pass_data['CAL_DUE'] = Asset.objects.filter(
            Q(calstat='OVER DUE') & Q(assetid__startswith='CH')).count()
        return render(request, 'wo_userApproval.html', pass_data)

    woid_list = [woid.strip() for woid in woids.split(',')]
    attended_time = request.POST.get('wo_attended')

    # Filter workbooks that are RELEASED
    releasable_workbooks = Workbook.objects.filter(
        wo_id__in=woid_list, status="WATUSRAPR")

    if releasable_workbooks.count() != len(woid_list):
        rDept = request.user.last_name.strip()
        worklist = Workbook.objects.filter(
            Q(status='WATUSRAPR') &
            Q(reportingDept=rDept) &
            Q(wotype='CM'))

        user_group = None
        for group in request.user.groups.all():
            user_group = group.name

        pass_data = woUserapprovepass_data(user_group, worklist)
        pass_data['user_group'] = user_group
        pass_data['datenow'] = timezone.now()
        pass_data['message'] = "Some selected work orders are not in 'RELEASED' status. No changes made.!!!"
        pass_data['error'] = True
        pass_data['PPM_DUE'] = Asset.objects.filter(
            Q(pmstat='OVER DUE') & Q(assetid__startswith='CH')).count()
        pass_data['CAL_DUE'] = Asset.objects.filter(
            Q(calstat='OVER DUE') & Q(assetid__startswith='CH')).count()
        return render(request, 'wo_userApproval.html', pass_data)

    canvas_data = request.POST.get('canvas_data', None)
    if canvas_data:
        format, imgstr = canvas_data.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
    # do something with the image file
    else:
        return HttpResponse(status=505)
    try:
        for wb in releasable_workbooks:
            wb.usersign = data
            wb.woapprover = request.user.username
            wb.status = 'CLOSED'
            wb.save()
            # updated_count = releasable_workbooks.update(usersign = data,woapprover = request.user.username,status = 'CLOSED')

    except DatabaseError as e:
        messages.error(request, f"Database update failed: {e}")

    rDept = request.user.last_name.strip()
    worklist = Workbook.objects.filter(
        Q(status='WATUSRAPR') &
        Q(reportingDept=rDept) &
        Q(wotype='CM'))

    user_group = None
    for group in request.user.groups.all():
        user_group = group.name

    pass_data = woUserapprovepass_data(user_group, worklist)
    pass_data['user_group'] = user_group
    pass_data['datenow'] = timezone.now()
    pass_data['message'] = "Work Order Assinged Succesfully!!!"
    pass_data['success'] = True
    pass_data['PPM_DUE'] = Asset.objects.filter(
        Q(pmstat='OVER DUE') & Q(assetid__startswith='CH')).count()
    pass_data['CAL_DUE'] = Asset.objects.filter(
        Q(calstat='OVER DUE') & Q(assetid__startswith='CH')).count()
    return render(request, 'wo_userApproval.html', pass_data)
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
@allowed_users('BMEADMIN')
def woGroupAssign(request):
    woids = request.POST.get('selectedwo')
    eng_id = request.POST.get('eng_id')

    if not woids:
        messages.error(request, "No work orders were selected.")
        worklist = Workbook.objects.all()
        user_group = None
        for group in request.user.groups.all():
            user_group = group.name

        pass_data = get_woviewpass_data(user_group, worklist)
        pass_data['user_group'] = user_group
        pass_data['datenow'] = datetime.now()
        pass_data['message'] = "No work orders were selected..!!!"
        pass_data['error'] = True
        pass_data['PPM_DUE'] = Asset.objects.filter(
            Q(pmstat='OVER DUE') & Q(assetid__startswith='CH')).count()
        pass_data['CAL_DUE'] = Asset.objects.filter(
            Q(calstat='OVER DUE') & Q(assetid__startswith='CH')).count()
        return render(request, 'viewwo.html', pass_data)

    woid_list = [woid.strip() for woid in woids.split(',')]
    attended_time = request.POST.get('wo_attended')

    # Filter workbooks that are RELEASED
    releasable_workbooks = Workbook.objects.filter(
        wo_id__in=woid_list, status="RELEASED")

    if releasable_workbooks.count() != len(woid_list):
        worklist = Workbook.objects.all()
        user_group = None
        for group in request.user.groups.all():
            user_group = group.name

        pass_data = get_woviewpass_data(user_group, worklist)
        pass_data['user_group'] = user_group
        pass_data['datenow'] = datetime.now()
        pass_data['message'] = "Some selected work orders are not in 'RELEASED' status. No changes made.!!!"
        pass_data['error'] = True
        pass_data['PPM_DUE'] = Asset.objects.filter(
            Q(pmstat='OVER DUE') & Q(assetid__startswith='CH')).count()
        pass_data['CAL_DUE'] = Asset.objects.filter(
            Q(calstat='OVER DUE') & Q(assetid__startswith='CH')).count()
        return render(request, 'work_list.html', pass_data)

    try:
        updated_count = releasable_workbooks.update(
            eng_id=eng_id,
            wo_attended=attended_time,
            status='ASSIGNED'
        )

    except DatabaseError as e:
        messages.error(request, f"Database update failed: {e}")

    worklist = Workbook.objects.all()
    user_group = None
    for group in request.user.groups.all():
        user_group = group.name

    pass_data = get_woviewpass_data(user_group, worklist)
    pass_data['user_group'] = user_group
    pass_data['datenow'] = datetime.now()
    pass_data['message'] = "Work Order Assinged Succesfully!!!"
    pass_data['success'] = True
    pass_data['PPM_DUE'] = Asset.objects.filter(
        Q(pmstat='OVER DUE') & Q(assetid__startswith='CH')).count()
    pass_data['CAL_DUE'] = Asset.objects.filter(
        Q(calstat='OVER DUE') & Q(assetid__startswith='CH')).count()
    return render(request, 'work_list.html', pass_data)
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
@allowed_users(bmeteam)
def ppm_Wo(request):
    keyid = request.GET.get('keyid')
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////


@login_required(login_url="/login/")
@allowed_users(bmeteam)
def filter_wo(request):
    keyid = request.GET.get('keyid')
    if keyid:
        worklist = Workbook.objects.filter(status=keyid)
    else:
        worklist = Workbook.objects.all()
    user_group = None
    for group in request.user.groups.all():
        user_group = group.name

    pass_data = get_woviewpass_data(user_group, worklist)
    pass_data['user_group'] = user_group
    pass_data['datenow'] = timezone.now()
    pass_data['PPM_DUE'] = Asset.objects.filter(
        Q(pmstat='OVER DUE') & Q(assetid__startswith='CH')).count()
    pass_data['CAL_DUE'] = Asset.objects.filter(
        Q(calstat='OVER DUE') & Q(assetid__startswith='CH')).count()
    return render(request, 'viewwo.html', pass_data)
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
@allowed_users(bmeteam)
def myWork(request):
    current_user = request.user
    worklist = Workbook.objects.filter(
        eng_id__icontains=current_user, status__in=["ASSIGNED", "WTNGAPR", "WTNGCOMPANY", "WTNGPART"])
    user_group = None
    for group in request.user.groups.all():
        user_group = group.name

    # Get success message from messages
    storage = get_messages(request)
    success_message = None
    for message in storage:
        if 'Work Completed Succesfully!!!' in message.message:
            success_message = True

    # Pass the message to the context if it exists
    pass_data = get_myWorkpass_data(user_group, worklist)
    pass_data['user_group'] = user_group
    if success_message:
        pass_data['success'] = True
        pass_data['message'] = "Work Completed Succesfully!!!"

    return render(request, 'myWork.html', pass_data)
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
@allowed_users(bmeteam)
def attendwo(request, id):
    if request.method == 'POST':
        action = request.POST.get('action')
        workbook = get_object_or_404(Workbook, wo_id=id)
        asset_id = workbook.asset_id
        worktype = workbook.wotype
        canvas_data = request.POST.get('canvas_data', None)
        parts = request.POST.get('parts')
        cost = request.POST.get('partscost')
        if parts:
            spare_parts = request.POST.get('parts')
            workbook.parts_description = spare_parts
        if cost:
            spare_cost = request.POST.get('partscost')
            workbook.parts_cost = spare_cost
        if canvas_data:
            format, imgstr = canvas_data.split(';base64,')
            ext = format.split('/')[-1]
            signdata = ContentFile(
                base64.b64decode(imgstr), name='temp.' + ext)
        else:
            return HttpResponse(status=505)

        for file in request.FILES.getlist('Work_Doc'):
            WorkDocument.objects.create(
                workbook=workbook, asset_id=asset_id, document=file)

        workbook.eng_sign = signdata
        if request.POST.get('status') == "WATUSRAPR":
            workDone = request.POST.get('wo_done')
            rsndtime = request.POST.get('rsndtime')
            downtime = request.POST.get('downtime')
            woDone = datetime.strptime(workDone, '%Y-%m-%dT%H:%M')
            woDone = timezone.make_aware(woDone)
            workbook.rsndtime = rsndtime
            workbook.downtime = downtime
            workbook.action = action
            workbook.wo_done = woDone
            
            workbook.status = 'CLOSED' if worktype in ('PPM', 'CAL') else request.POST.get('status')
            ######## If work Order is PPM then update next PPM MONTH , PPM Done#####################
            if worktype == "PPM":
                assetinfo = get_object_or_404(Asset, assetid = asset_id)
                ppmmonths = assetinfo.pmmonth
                date_obj = request.POST.get('wo_done')
                new_pmdue = next_ppmMonth(date_obj,ppmmonths)
                assetinfo.pmdone = datetime.strptime(workDone, '%Y-%m-%dT%H:%M')
                assetinfo.pmdue = new_pmdue
                assetinfo.pmstat = 'NOT DUE'
                assetinfo.save()
            ######## If work Order is CAL then update next CAL MONTH , CAL Done##################### 
            if worktype == "CAL":
                assetinfo = get_object_or_404(Asset, assetid = asset_id)
                calmonths = assetinfo.calmonth
                date_obj = request.POST.get('wo_done')
                new_pmdue = next_ppmMonth(date_obj,calmonths)
                assetinfo.caldone = datetime.strptime(workDone, '%Y-%m-%dT%H:%M')
                assetinfo.caldue = new_pmdue
                assetinfo.calstat = 'NOT DUE'
                assetinfo.save()
        else:
            current_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            # Ensure action is appended to existing content 'WATUSRAPR'
            if workbook.action:
                workbook.action = f"{workbook.action.rstrip('. ')}. {action}. {current_time}"
            else:
                workbook.action = f"{action}. {current_time}"

            workbook.status = request.POST.get('status')

        workbook.save()

        current_user = request.user
        worklist = Workbook.objects.filter(
            eng_id__icontains=current_user, status__in=["ASSIGNED", "WTNGAPR", "WTNGCOMPANY", "WTNGPART"])
        user_group = None
        for group in request.user.groups.all():
            user_group = group.name

        pass_data = get_myWorkpass_data(user_group, worklist)
        pass_data['user_group'] = user_group
        pass_data['message'] = "Work Completed Succesfully!!!"
        pass_data['success'] = True
        messages.success(request, "Work Completed Succesfully!!!")
        messages.add_message(request, messages.SUCCESS, 'Success: true')
        return redirect('myWork')
    else:
        current_user = request.user
        workbook = get_object_or_404(Workbook, wo_id=id)
        worklist = Workbook.objects.filter(
            eng_id__icontains=current_user, status__in=["ASSIGNED", "WTNGAPR", "WTNGCOMPANY", "WTNGPART"])
        user_group = None
        for group in request.user.groups.all():
            user_group = group.name

        pass_data = get_myWorkpass_data(user_group, worklist)
        pass_data['user_group'] = user_group
        pass_data['description'] = workbook.description
        pass_data['wo_date'] = workbook.wo_date
        pass_data['wo_attended'] = workbook.wo_attended
        return render(request, 'attendwo.html', pass_data)
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
def get_work_documents(request):
    work_id = request.GET.get('work_id')
    work_id = work_id.replace('WO-', '')
    if work_id:
        docs = WorkDocument.objects.filter(workbook_id=work_id)
        data = [{'url': doc.document.url, 'asset_id': doc.asset_id}
                for doc in docs]
        return JsonResponse({'status': 'success', 'documents': data})
    return JsonResponse({'status': 'error', 'message': 'Missing work_id'})
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
@allowed_users(viewSr)
def generate_service_report(request, wo_id):
    # Get the workbook object or return 404
    workbook = get_object_or_404(Workbook, wo_id=wo_id)

    # Prepare context data
    context = {
        'workbook': workbook,
        # Replace with your actual institution name
        'institution_name': 'INSTITUTION NAME',
        # Replace with your actual address
        'address': '123 Main Street<br>City, State<br>ZIP Code, Country',
        # Replace with your actual logo path
        'logo_path': os.path.join(settings.MEDIA_URL, 'LLL.jpeg'),
    }

    # Render the HTML template with context
    html_string = render_to_string('SR.html', context)

    # Return as HTML response (you could also generate PDF here if needed)
    return HttpResponse(html_string)
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////


def search_woid(request):
    if request.method == 'POST':
        wo_id = request.POST.get('wo_id')
        try:
            workbook = Workbook.objects.get(wo_id=wo_id)
            return redirect('edit_workbook', pk=workbook.pk)
        except Workbook.DoesNotExist:
            return render(request, 'search_woid.html', {'error': f'WO ID "{wo_id}" not found'})
    return render(request, 'search_woid.html')


def edit_workbooktst(request, pk):
    workbook = get_object_or_404(Workbook, pk=pk)
    workdocs = WorkDocument.objects.filter(workbook=workbook)

    if request.method == 'POST':
        form = WorkbookForm(request.POST, request.FILES, instance=workbook)
        formset = WorkDocumentFormSet(
            request.POST, request.FILES, queryset=workdocs)

        if form.is_valid() and formset.is_valid():
            form.save()
            workdoc_instances = formset.save(commit=False)
            for instance in workdoc_instances:
                instance.workbook = workbook
                instance.save()
            for deleted_form in formset.deleted_objects:
                deleted_form.delete()
            # Or redirect to a success page
            return redirect('edit_workbook', pk=workbook.pk)

    else:
        form = WorkbookForm(instance=workbook)
        formset = WorkDocumentFormSet(queryset=workdocs)

    return render(request, 'edit_workbook.html', {
        'form': form,
        'workdoc_formset': formset
    })
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
@allowed_users(gtapprove)
def gatepass(request):
    # gatepass = Gatepass.objects.all()
    # gt = gatepass.first()
    # gatepass = Gatepass.objects.order_by('pass_id', 'id').distinct('pass_id')

    returnable = Gatepass.objects.filter(status='SEND_OUT',gatepasstype='RETURNABLE').values('pass_id').distinct().count()
    returned = Gatepass.objects.filter(status='RETURNED',gatepasstype='RETURNABLE').values('pass_id').distinct().count()
    nonreturnable = Gatepass.objects.filter(status='SEND_OUT',gatepasstype='NON-RETURNABLE').values('pass_id').distinct().count()

    # Annotate to get the minimum ID for each pass_id
    first_gatepass_per_passid = Gatepass.objects.values('pass_id').annotate(min_id=Min('id'))
    # Filter the Gatepass table to include only the rows with these minimum IDs
    gatepass = Gatepass.objects.filter(
        id__in=[item['min_id'] for item in first_gatepass_per_passid])

    if request.method == 'POST':
        current_user = request.user
        for group in current_user.groups.all():
            user_group = group.name

        pass_data = get_gatepass_data(user_group, gatepass)
        pass_data['user_group'] = user_group
        return render(request, 'gatePass.html', pass_data)
    else:
        if request.GET.get('keyid'):
            keyid = request.GET.get('keyid')
            if keyid == "returned":
                gatepass = Gatepass.objects.filter(id__in=[item['min_id'] for item in first_gatepass_per_passid],
                            status="RETURNED")
            if keyid == "nonreturned":
                gatepass = Gatepass.objects.filter(id__in=[item['min_id'] for item in first_gatepass_per_passid],
                            status="SEND_OUT",gatepasstype="RETURNABLE")
            
        current_user = request.user
        for group in current_user.groups.all():
            user_group = group.name

        pass_data = get_gatepass_data(user_group, gatepass)
        pass_data['user_group'] = user_group
        pass_data['returnable'] = returnable
        pass_data['nonreturnable'] = nonreturnable
        pass_data['returned'] = returned
        for entry in first_gatepass_per_passid:
            gatepass = Gatepass.objects.get(id=entry['min_id'])
            pass_data['stat'] = gatepass.status
        return render(request, 'gatePass.html', pass_data)

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
@allowed_users(bmeteam)
def gatepassform(request):

    # Annotate to get the minimum ID for each pass_id
    first_gatepass_per_passid = Gatepass.objects.values(
        'pass_id').annotate(min_id=Min('id'))
    # Filter the Gatepass table to include only the rows with these minimum IDs
    gatepass = Gatepass.objects.filter(
        id__in=[item['min_id'] for item in first_gatepass_per_passid])

    # Ensure GP_formset is always initialized
    GP_formset = None
    GP_formset = formset_factory(GatepassForm, extra=1)
    # YourModelFormSet = modelformset_factory(Gatepass,form=GatepassForm,extra=1)

    if request.method == 'POST':
        formset = GP_formset(request.POST, request.FILES, prefix='gtp')
        if formset.is_valid():
            num = 0
            gpt_dic = {}
            for form in formset:
                canvas_data1 = request.POST.get('canvas_data1', None)
                canvas_data2 = request.POST.get('canvas_data2', None)
                gtpid = request.POST.get('gtpid')
                gtp_date = request.POST.get('gtp_date')

                naive_datetime = datetime.strptime(gtp_date, "%Y-%m-%dT%H:%M")
                gtp_date = timezone.make_aware(naive_datetime)
                collected_by = request.POST.get('collected_by')
                contact_num = request.POST.get('contact_num')
                gtp_to = request.POST.get('gtp_to')
                send_by = request.POST.get('send_by')
                gttype = request.POST.get('gttype')
                asset_name = request.POST.get(f"gtp-{num}-asset_name")
                UOQ = request.POST.get(f"gtp-{num}-UOQ")
                qty = request.POST.get(f"gtp-{num}-qty")
                asset = request.POST.get(f"gtp-{num}-asset")
                serial = request.POST.get(f"gtp-{num}-serial")
                reason = request.POST.get(f"gtp-{num}-reason")

                if canvas_data1:
                    format, imgstr = canvas_data1.split(';base64,')
                    ext = format.split('/')[-1]
                    sign_data1 = ContentFile(
                        base64.b64decode(imgstr), name='temp.' + ext)
                else:
                    return HttpResponse(status=505)

                if canvas_data2:
                    format, imgstr = canvas_data2.split(';base64,')
                    ext = format.split('/')[-1]
                    sign_data2 = ContentFile(
                        base64.b64decode(imgstr), name='temp.' + ext)
                else:
                    return HttpResponse(status=505)

                gpt_dic[num] = {
                    'pass_id': gtpid,
                    'asset_name': asset_name,
                    'collector_name': collected_by,
                    'contact_num': contact_num,
                    'sender_name': send_by,
                    'send_to': gtp_to,
                    'gatepasstype' : gttype,
                    'uoq': UOQ,
                    'asset': asset,
                    'serial': serial,
                    'qty': qty,
                    'description': reason,
                    'out_date': gtp_date,
                    'collector_sign': sign_data1,
                    'bme_sign': sign_data2,
                    'status': 'ADMIN_Approval_Pending',
                }
                num += 1

            try:
                for data in gpt_dic.values():
                    Gatepass.objects.create(**data)
            except Exception as e:
                current_user = request.user
                for group in request.user.groups.all():
                    user_group = group.name

                pass_data = get_gatepass_data(user_group, gatepass)
                pass_data['error'] = True
                pass_data['message'] = "Error!!!"
                pass_data['user_group'] = user_group
                return render(request, 'gatePass.html', pass_data)

            current_user = request.user
            for group in request.user.groups.all():
                user_group = group.name

            pass_data = get_gatepass_data(user_group, gatepass)
            pass_data['success'] = True
            pass_data['message'] = "Success!!!"
            pass_data['user_group'] = user_group
            return render(request, 'gatePass.html', pass_data)
        else:
            current_user = request.user
            for group in request.user.groups.all():
                user_group = group.name

            pass_data = get_gatepass_data(user_group, gatepass)
            pass_data['error'] = True
            pass_data['message'] = "Invalid Form Data!"
            pass_data['user_group'] = user_group
            return render(request, 'gatePass.html', pass_data)

    if request.method == 'GET':

        latest_gatepass = Gatepass.objects.latest(
            'pk') if Gatepass.objects.exists() else None
        gtpid = f"GTP-{int(latest_gatepass.pass_id.split('-')
                           [1]) + 1}" if latest_gatepass else "GTP-0"

        current_user = request.user
        for group in request.user.groups.all():
            user_group = group.name
        # pass_data['formset'] = GP_formset(prefix='gtp')
        pass_data = get_gatepass_data(user_group, gatepass)
        pass_data['user_group'] = user_group

        formset = GP_formset(prefix='gtp')
        pass_data['gtpid'] = gtpid
        context = {'formset': formset}
        # Add all items from `pass_data` to the context
        context.update(pass_data)
        return render(request, 'gatePass_form.html', context)
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
@allowed_users(gtapprove)
def gatepassAdmin(request):

    if request.method == 'POST':
        form = GatepassApproval(request.POST, request.FILES)
        if form.is_valid():
            # Use cleaned_data to get form values
            pass_id = form.cleaned_data['pass_id']
            # Assuming the admin sign is uploaded
            admin_sign = request.POST.get('admin_sign', None)
            # Assuming the status is provided in the form
            status = form.cleaned_data['status']
            if admin_sign:
                format, imgstr = admin_sign.split(';base64,')
                ext = format.split('/')[-1]
                sign_data = ContentFile(
                    base64.b64decode(imgstr), name='temp.' + ext)
            else:
                return HttpResponse(status=505)

            gatepasses = Gatepass.objects.filter(pass_id=pass_id)

            for gatepass in gatepasses:
                gatepass.admin_sign = sign_data
                gatepass.status = status
                gatepass.save()

            current_user = request.user
            for group in current_user.groups.all():
                user_group = group.name

            first_gatepass_per_passid = Gatepass.objects.values(
                'pass_id').annotate(min_id=Min('id'))
            # Filter the Gatepass table to include only the rows with these minimum IDs
            gatepass = Gatepass.objects.filter(
                id__in=[item['min_id'] for item in first_gatepass_per_passid])

            pass_data = get_gatepass_data(user_group, gatepass)
            pass_data['user_group'] = user_group
            pass_data['success'] = True
            pass_data['message'] = "Success!!!"
            pass_data['user_group'] = user_group
            for entry in first_gatepass_per_passid:
                gatepass = Gatepass.objects.get(id=entry['min_id'])
            return render(request, 'gatePass.html', pass_data)
        else:
            first_gatepass_per_passid = Gatepass.objects.values(
                'pass_id').annotate(min_id=Min('id'))
            # Filter the Gatepass table to include only the rows with these minimum IDs
            gatepass = Gatepass.objects.filter(
                id__in=[item['min_id'] for item in first_gatepass_per_passid])

            pass_data = get_gatepass_data(user_group, gatepass)
            pass_data['user_group'] = user_group
            pass_data['error'] = True
            pass_data['message'] = "Error!!!"
            pass_data['user_group'] = user_group
            for entry in first_gatepass_per_passid:
                gatepass = Gatepass.objects.get(id=entry['min_id'])
            return render(request, 'gatePass.html', pass_data)
    else:
        first_gatepass_per_passid = Gatepass.objects.values(
            'pass_id').annotate(min_id=Min('id'))
        # Filter the Gatepass table to include only the rows with these minimum IDs
        gatepass = Gatepass.objects.filter(
            id__in=[item['min_id'] for item in first_gatepass_per_passid])

        pass_data = get_gatepass_data(user_group, gatepass)
        pass_data['user_group'] = user_group
        pass_data['success'] = True
        pass_data['message'] = "Success!!!"
        pass_data['user_group'] = user_group
        for entry in first_gatepass_per_passid:
            gatepass = Gatepass.objects.get(id=entry['min_id'])
        return render(request, 'gatePass.html', pass_data)
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
@allowed_users(gtapprove)
def gtSendout(request):

    if request.method == 'POST':
        form = gtSend(request.POST, request.FILES)
        if form.is_valid():
            # Use cleaned_data to get form values
            pass_id = form.cleaned_data['pass_id']
            # Assuming the admin sign is uploaded
            send_out_date = form.cleaned_data['out_date']
            gatepasses = Gatepass.objects.filter(pass_id=pass_id)

            try:
                for gatepass in gatepasses:
                    gatepass.out_date = send_out_date
                    gatepass.status = "SEND_OUT"
                    gatepass.save()
            except Exception as e:
                return HttpResponse(status=505)

            first_gatepass_per_passid = Gatepass.objects.values(
                'pass_id').annotate(min_id=Min('id'))
            # Filter the Gatepass table to include only the rows with these minimum IDs
            gatepass = Gatepass.objects.filter(
                id__in=[item['min_id'] for item in first_gatepass_per_passid])

            current_user = request.user
            for group in current_user.groups.all():
                user_group = group.name

            pass_data = get_gatepass_data(user_group, gatepass)
            pass_data['user_group'] = user_group
            pass_data['success'] = True
            pass_data['message'] = "success!!!"
            pass_data['user_group'] = user_group
            for entry in first_gatepass_per_passid:
                gatepass = Gatepass.objects.get(id=entry['min_id'])
            return render(request, 'gatePass.html', pass_data)
        else:
            first_gatepass_per_passid = Gatepass.objects.values(
                'pass_id').annotate(min_id=Min('id'))
            # Filter the Gatepass table to include only the rows with these minimum IDs
            gatepass = Gatepass.objects.filter(
                id__in=[item['min_id'] for item in first_gatepass_per_passid])

            current_user = request.user
            for group in current_user.groups.all():
                user_group = group.name

            pass_data = get_gatepass_data(user_group, gatepass)
            pass_data['user_group'] = user_group
            pass_data['error'] = True
            pass_data['message'] = "Error!!!"
            pass_data['user_group'] = user_group
            for entry in first_gatepass_per_passid:
                gatepass = Gatepass.objects.get(id=entry['min_id'])
            return render(request, 'gatePass.html', pass_data)
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
# # ///////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
@allowed_users(gtapprove)
def gatepass_print(request, pass_id):
    try:
        # Retrieve the specific Gatepass record
        gatepasses = Gatepass.objects.filter(pass_id=pass_id)

        if gatepasses.exists():
            first_gatepass = gatepasses.first()

    except Gatepass.DoesNotExist:
        return HttpResponse("Gatepass record not found", status=404)

    return render(request, 'gatepass_print.html', {'gatepasses': gatepasses, 'first_gatepass': first_gatepass})

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
def gatePass_ajax(request, id):

    try:
        # Retrieve the specific Gatepass record
        gatepasses = Gatepass.objects.filter(pass_id=id)

        if gatepasses.exists():
            first_gatepass = gatepasses.first()
            # Serialize the gatepass instance
            serializer = GatepassSerializer(first_gatepass)
            return JsonResponse({'gtp_data': serializer.data})

    except Gatepass.DoesNotExist:
        return HttpResponse("Gatepass record not found", status=404)
    getpdata = {'gtp_data': first_gatepass,
                }
    return JsonResponse(getpdata)
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
def gtSend_ajax(request):
    if request.method == 'POST':
        status = "SEND_OUT"
        date_out = datetime.now()
        pass_id = request.POST.get('pass_id')

        # Save the data to the model
        gatepasses = Gatepass.objects.filter(pass_id=pass_id)
        try:
            for gatepass in gatepasses:
                gatepass.status = status
                gatepass.out_date = date_out
                gatepass.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False})

    return JsonResponse({'success': False})
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////

# /////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////


class WorkbookListView(APIView):
    def get(self, request):
        workbooks = Workbook.objects.all()  # Get all workbook entries
        serializer = WorkbookSerializer(workbooks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
# //////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
@allowed_users(prcreate)
def prtable(request):
    prdata = PRR.objects.all()
    if request.method == 'POST':
        if PRR.objects.exists():
            last_pk = PRR.objects.latest('pk').pk
        else:
            last_pk = 0

        canvas_data = request.POST.get('canvas_data', None)
        if canvas_data:
            format, imgstr = canvas_data.split(';base64,')
            ext = format.split('/')[-1]
            signdata = ContentFile(
                base64.b64decode(imgstr), name='temp.' + ext)
            # do something with the image file
        else:
            return HttpResponse(status=505)

        prid = 'PR-'+str(last_pk+1)
        pr_form = prCreateform(request.POST)

        if pr_form.is_valid():
            prform = pr_form.save(commit=False)
            prform.PRN = prid
            prform.User_Date = timezone.now()
            prform.User_Sign = signdata
            prform.save()

        else:
            current_user = request.user
            for group in current_user.groups.all():
                user_group = group.name
            pass_data = pr_pass_data(user_group, prdata)
            pass_data['user_group'] = user_group
            pass_data['error'] = True
            pass_data['message'] = "Error!!!"
            return render(request, 'prTable.html', pass_data)

        current_user = request.user
        for group in current_user.groups.all():
            user_group = group.name
        pass_data = pr_pass_data(user_group, prdata)
        pass_data['user_group'] = user_group
        pass_data['success'] = True
        pass_data['message'] = "success!!!"
        return render(request, 'prTable.html', pass_data)

    else:
        current_user = request.user
        for group in current_user.groups.all():
            user_group = group.name
        pass_data = pr_pass_data(user_group, prdata)
        pass_data['user_group'] = user_group
        return render(request, 'prTable.html', pass_data)
# # ///////////////////////////////////////////////////////////////////////////////////////////////////////////
# # //////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
@allowed_users(prcreate)
def pr_print(request, prId):
    try:
        # Retrieve the specific Gatepass record
        prdata = PRR.objects.get(PRN=prId)

    except Gatepass.DoesNotExist:
        return HttpResponse("Gatepass record not found", status=404)

    return render(request, 'pr_print.html', {'prdata': prdata})

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
@allowed_users(prapprove)
def pr_approve(request, PR_No=None):

    if request.method == 'POST':
        current_user = request.user
        for group in current_user.groups.all():
            user_group = group.name
    # ======================================================================#
        if user_group == "BMEADMIN":
            prdata = get_object_or_404(PRR, PRN=PR_No)

            canvas_data = request.POST.get('bme_sign', None)
            if canvas_data:
                format, imgstr = canvas_data.split(';base64,')
                ext = format.split('/')[-1]
                signdata = ContentFile(
                    base64.b64decode(imgstr), name='temp.' + ext)
            else:
                return HttpResponse(status=505)
            prdata.BME_Sign = signdata
            prdata.BME_Comment = request.POST.get('BMEComment')
            prdata.BME_Date = timezone.now()
            prdata.status = request.POST.get('Action')
            try:
                prdata.full_clean()
            except ValidationError as e:
                return HttpResponse(status=505)

            # 5. Save with transaction
            with transaction.atomic():
                prdata.save()
                prdata = PRR.objects.filter(status="REQUESTED")
                pass_data = pr_apr_pass(user_group, prdata)
                pass_data['user_group'] = user_group
                pass_data['success'] = True
                pass_data['message'] = "success!!!"
                return render(request, 'prAprTable.html', pass_data)
        # ======================================================================#
        elif user_group == "MANAGEMENT":

            prdata = get_object_or_404(PRR, PRN=PR_No)

            canvas_data = request.POST.get('admin_sign', None)
            if canvas_data:
                format, imgstr = canvas_data.split(';base64,')
                ext = format.split('/')[-1]
                signdata = ContentFile(
                    base64.b64decode(imgstr), name='temp.' + ext)
            else:
                return HttpResponse(status=505)
            prdata.Admin_Sign = signdata
            prdata.Admin_Comment = request.POST.get('AdminComment')
            prdata.Admin_Date = timezone.now()
            prdata.status = request.POST.get('Action')


            try:
                prdata.full_clean()
            except ValidationError as e:
                return HttpResponse(status=505)

            # 5. Save with transaction
            with transaction.atomic():
                prdata.save()
                prdata = PRR.objects.filter(
                    status__in=["BMEApproved", "BMERejected"])
                pass_data = pr_apr_pass(user_group, prdata)
                pass_data['user_group'] = user_group
                pass_data['success'] = True
                pass_data['message'] = "success!!!"
                return render(request, 'prAprTable.html', pass_data)
    else:
        current_user = request.user
        for group in current_user.groups.all():
            user_group = group.name
        if user_group == "BMEADMIN":
            prdata = PRR.objects.filter(status__in=["REQUESTED"])
            pass_data = pr_apr_pass(user_group, prdata)
            pass_data['user_group'] = user_group
            return render(request, 'prAprTable.html', pass_data)

        elif user_group == "MANAGEMENT":
            prdata = PRR.objects.filter(
                status__in=["BMEApproved", "BMERejected"])
            pass_data = pr_apr_pass(user_group, prdata)
            pass_data['user_group'] = user_group
            return render(request, 'prAprTable.html', pass_data)
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
@allowed_users('BMEADMIN')
def monthly_report(request):
    form = ReportFilterForm(request.GET or None)
    context = {
        'form': form,
        'labels': [],
        'avg_downtime_data': [],
        'avg_rsndtime_data': [],
        'zipped_data': [],
        'sidebar_template': 'sidebar.html',
        'hovered6': "hovered"
    }

    if form.is_valid():
        asset_type = form.cleaned_data['asset_type']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']

        # Create datetime objects with timezone awareness
        start_dt = make_aware(datetime.combine(start_date, time.min))
        end_dt = make_aware(datetime.combine(end_date, time.max))

        queryset = Workbook.objects.filter(
            asset_type=asset_type,
            wo_done__range=(start_dt, end_dt)
        )

        monthly_data = defaultdict(lambda: {'downtime': [], 'rsndtime': []})

        for obj in queryset:
            if obj.wo_done:
                month_str = obj.wo_done.strftime('%Y-%m')
                if obj.downtime:
                    monthly_data[month_str]['downtime'].append(obj.downtime)
                if obj.rsndtime:
                    monthly_data[month_str]['rsndtime'].append(obj.rsndtime)

        for month in sorted(monthly_data):
            downtime = monthly_data[month]['downtime']
            rsndtime = monthly_data[month]['rsndtime']

            avg_dt = round(sum(downtime)/len(downtime), 2) if downtime else 0
            avg_rt = round(sum(rsndtime)/len(rsndtime), 2) if rsndtime else 0

            context['labels'].append(month)
            context['avg_downtime_data'].append(avg_dt)
            context['avg_rsndtime_data'].append(avg_rt)
            context['zipped_data'].append((month, avg_dt, avg_rt))

    return render(request, 'monthly_report.html', context)
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
def utilities(request):
    return render(request, 'utilities.html',{'sidebar_template': "sidebar.html", 'hovered11': "hovered"})

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////

User = get_user_model()

class LoginView(APIView):
    def post(self, request):
        u = request.data.get('username')
        p = request.data.get('password')
        user = authenticate(username=u, password=p)
        if user:
            return Response({'user_id': user.id})
        return Response({'error':'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class SaveToken(APIView):
    def post(self, request):
        user = User.objects.get(pk=request.data['user_id'])
        token = request.data['fcm_token']
        FCMDevice.objects.update_or_create(user=user, registration_id=token, defaults={'type':'android'})
        return Response({'status':'ok'})
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
@allowed_users('BMEADMIN')
def PPMGeneration(request):
    logger = logging.getLogger(__name__)
    today = date.today()

    assetlist = Asset.objects.exclude(pmdue__isnull=True).exclude(pmdue='').exclude(pmstat='NOT DUE')
    
    logger.info(f"{assetlist.count()} assets found with 'OVER DUE'")

    result = today.strftime('%b').upper() + f'{today.year}'
    created_count = 0

    for item in assetlist:
        logger.info(f"Checking asset {item.assetid} with LPMG {item.LPMG} against {result}")
        if item.LPMG != result:
            ppmWOSTAT = add_pmwo(item.assetid)
            item.LPMG = result
            item.save()
            logger.info(f"PPM Generation result for {item.assetid}: {ppmWOSTAT}")
            created_count += 1

    logger.info(f"PPM Generation completed. Total work orders created: {created_count}")
    return redirect(index)

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
@csrf_exempt
def check_location_exists(request):
    if request.method == 'POST':
        location = request.POST.get('location', '').strip()
        exists = Departments.objects.filter(LOCATION__iexact=location).exists()
        return JsonResponse({'exists': exists})
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////


def add_department(request):
    pass_data = {}
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save(commit=False)
            
            # Get the last PK
            last = Departments.objects.order_by('-pk').first()
            next_id = last.pk + 1 if last else 1

            department.LCNID = f"LCN-{next_id}"
            department.PARENT_DEPT = department.LOCATION
            department.save()

            pass_data['success'] = True
            pass_data['message'] = "success!!!"
            pass_data['sidebar_template'] = "sidebar.html"
            pass_data['hovered11'] = "hovered"
            return render(request, 'utilities.html', pass_data)
        else:
            pass_data['error'] = True
            pass_data['message'] = "Form Error!!!"
            pass_data['sidebar_template'] = "sidebar.html"
            pass_data['hovered11'] = "hovered"
            return render(request, 'utilities.html', pass_data)
    else:
        pass_data['sidebar_template'] = "sidebar.html"
        pass_data['hovered11'] = "hovered"
        return render(request, 'utilities.html', pass_data)

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
def pmpage(request):
    user_group = None
    for group in request.user.groups.all():
        user_group = group.name

    sidebar_map = {'BMEADMIN': 'sidebar.html'}
    sidebar_template = sidebar_map.get(user_group)
    site_map = {'BMEADMIN': 'pmpage.html'}
    gotosite = site_map.get(user_group)
    group_data = {'BMEADMIN': {'sidebar_template': sidebar_template, 'hovered11': "hovered"}}

    storage = get_messages(request)
    message_list = [m.message for m in storage]
    pass_data = group_data.get(user_group)
    if pass_data is not None:
        if message_list:
            if message_list[0].lower().startswith('success'):
                pass_data['success'] = True
            else:
                pass_data['error'] = True
            pass_data['message'] = message_list[0]
            pass_data['message'] = message_list[0]  # Or all messages as list
    return render(request, gotosite, pass_data)
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
def pmtable_data(request):
    assetcat = request.GET.get('assettype')
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    sort_column = request.GET.get('sort_column', 'assetid')
    sort_direction = request.GET.get('sort_direction', 'asc')
    search_terms = json.loads(request.GET.get('search_terms', '[]'))

    allowed_columns = {
        'assetid', 'assetname', 'asset_make', 'asset_model',
        'slno', 'dept', 'pmdue' , 'pmstat'
    }
    if sort_column not in allowed_columns:
        sort_column = 'assetid'

    if assetcat=='MISSL':
        queryset = Asset.objects.filter(assetid__startswith=assetcat)
    else:
        queryset = Asset.objects.exclude(Q(assetid__iexact='nan') | Q(assetid__isnull=True))
        #queryset = queryset.filter(assetid__startswith='CH')

    # Apply column-specific searches
    for i, term in enumerate(search_terms):
        if term:
            field_map = {
                0: 'assetid',
                1: 'assetname',
                2: 'asset_make',
                3: 'asset_model',
                4: 'slno',
                5: 'dept',
                6: 'pmmonth',
                7: 'pmstat',
            }
            if i in field_map:
                field = field_map[i]
                queryset = queryset.filter(**{f'{field}__icontains': term})

    records_total = Asset.objects.count()
    records_filtered = queryset.count()    
    assets = list(queryset)

    if sort_column == 'assetid':
        # Sort in Python using numeric part of assetid
        assets.sort(
            key=lambda x: extract_numeric(x.assetid),
            reverse=(sort_direction == 'desc')
        )
    else:
        # Use default ORM ordering for other columns
        order_by = sort_column
        if sort_direction == 'desc':
            order_by = '-' + order_by
        assets = list(queryset.order_by(order_by))

    paginator = Paginator(assets, length)
    page_number = (start // length) + 1
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        page = paginator.page(1)

    data = []
    for asset in page:
        data.append({
            'assetid': asset.assetid,
            'assetname': asset.assetname or '',
            'asset_make': asset.asset_make or '',
            'asset_model': asset.asset_model or '',
            'slno': asset.slno or '',
            'dept': asset.dept or '',
            'pmmonth': asset.pmmonth or '',
            'pmstat': asset.pmstat or '',
            'action': f'<button class="btn btn-sm btn-info view-btn" data-id="{asset.assetid}">View</button>',
        })

    return JsonResponse({
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data,
    })
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
def pmedit(request):
    if request.method == 'POST':
        try:
            assetID = request.POST.get('asset_id')
            pmMonth = request.POST.get('pmmonth')
            wotype = 'PPM'
            today = date.today()
            formatted_date = today.strftime('%Y-%m-%d')
            new_pmdue = next_ppmMonthview(formatted_date,pmMonth)
            print(new_pmdue)
            assetData = Asset.objects.get(assetid = assetID)
            assetData.pmdue = new_pmdue
            assetData.pmmonth = pmMonth
            assetData.save()

            current_month = datetime.now().strftime('%b').upper()
            # Check if current month is in calMonth (handle spacing and case)
            if current_month in [m.strip().upper() for m in pmMonth.split(',')]:
                asset = Asset.objects.get(assetid=assetID)
                current_month_year = datetime.now().strftime('%b%Y').upper()
                if asset.LPMG == current_month_year:
                    messages.success(request, "Success!!! PM-WO Present!!!")
                    return redirect ('pmpage')
                else:
                    pmwostat = add_pmwoonly(assetID, wotype)
            else:
                messages.success(request, "Success!!!")
                return redirect ('pmpage')
            
            if pmwostat == "Success":
                asset.LPMG = current_month_year
                asset.save()
                messages.success(request, "Success!!!")
                return redirect ('pmpage')
            else:
                messages.error(request, "Error in WO!!!")
                return redirect ('pmpage')
        
        except Exception as e:
            # Catch-all for any other exceptions
            messages.error(request, f"An unexpected error occurred: {str(e)}")
            return redirect ('pmpage')
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
def calpage(request):
    user_group = None
    for group in request.user.groups.all():
        user_group = group.name

    sidebar_map = {'BMEADMIN': 'sidebar.html'}
    sidebar_template = sidebar_map.get(user_group)
    site_map = {'BMEADMIN': 'calpage.html'}
    gotosite = site_map.get(user_group)
    group_data = {'BMEADMIN': {'sidebar_template': sidebar_template, 'hovered11': "hovered"}}
    storage = get_messages(request)

    message_list = [m.message for m in storage]
    pass_data = group_data.get(user_group)
    if pass_data is not None:
        if message_list:
            if message_list[0].lower().startswith('success'):
                pass_data['success'] = True
            else:
                pass_data['error'] = True
            pass_data['message'] = message_list[0]
            pass_data['message'] = message_list[0]  # Or all messages as list
    return render(request, gotosite, pass_data)
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
def caltable_data(request):
    assetcat = request.GET.get('assettype')
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    sort_column = request.GET.get('sort_column', 'assetid')
    sort_direction = request.GET.get('sort_direction', 'asc')
    search_terms = json.loads(request.GET.get('search_terms', '[]'))

    allowed_columns = {
        'assetid', 'assetname', 'asset_make', 'asset_model',
        'slno', 'dept', 'calmonth' , 'calstat'
    }
    if sort_column not in allowed_columns:
        sort_column = 'assetid'

    if assetcat=='MISSL':
        queryset = Asset.objects.filter(assetid__startswith=assetcat)
    else:
        queryset = Asset.objects.exclude(Q(assetid__iexact='nan') | Q(assetid__isnull=True))
        #queryset = queryset.filter(assetid__startswith='CH')

    # Apply column-specific searches
    for i, term in enumerate(search_terms):
        if term:
            field_map = {
                0: 'assetid',
                1: 'assetname',
                2: 'asset_make',
                3: 'asset_model',
                4: 'slno',
                5: 'dept',
                6: 'calmonth',
                7: 'calstat',
            }
            if i in field_map:
                field = field_map[i]
                queryset = queryset.filter(**{f'{field}__icontains': term})

    records_total = Asset.objects.count()
    records_filtered = queryset.count()    
    assets = list(queryset)

    if sort_column == 'assetid':
        # Sort in Python using numeric part of assetid
        assets.sort(
            key=lambda x: extract_numeric(x.assetid),
            reverse=(sort_direction == 'desc')
        )
    else:
        # Use default ORM ordering for other columns
        order_by = sort_column
        if sort_direction == 'desc':
            order_by = '-' + order_by
        assets = list(queryset.order_by(order_by))

    paginator = Paginator(assets, length)
    page_number = (start // length) + 1
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        page = paginator.page(1)

    data = []
    for asset in page:
        data.append({
            'assetid': asset.assetid,
            'assetname': asset.assetname or '',
            'asset_make': asset.asset_make or '',
            'asset_model': asset.asset_model or '',
            'slno': asset.slno or '',
            'dept': asset.dept or '',
            'calmonth': asset.calmonth or '',
            'calstat': asset.calstat or '',
            'action': f'<button class="btn btn-sm btn-info view-btn" data-id="{asset.assetid}">View</button>',
        })

    return JsonResponse({
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data,
    })
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
def caledit(request):
    if request.method == 'POST':
        try:
            assetID = request.POST.get('asset_id')
            calMonth = request.POST.get('calmonth')
            wotype = 'CAL'
            today = date.today()
            formatted_date = today.strftime('%Y-%m-%d')
            new_caldue = next_ppmMonthview(formatted_date,calMonth)
            assetData = Asset.objects.get(assetid = assetID)
            assetData.caldue = new_caldue
            assetData.calmonth = calMonth
            assetData.save()

            current_month = datetime.now().strftime('%b').upper()
            # Check if current month is in calMonth (handle spacing and case)
            if current_month in [m.strip().upper() for m in calMonth.split(',')]:
                asset = Asset.objects.get(assetid=assetID)
                current_month_year = datetime.now().strftime('%b%Y').upper()
                if asset.LCALG == current_month_year:
                    messages.success(request, "Success!!! CAL-WO Present!!!")
                    return redirect ('calpage')
                else:
                    calwostat = add_calwoonly(assetID, wotype)
            else:
                messages.success(request, "Success!!!")
                return redirect ('calpage')
            
            if calwostat == "Success":
                asset.LCALG = current_month_year
                asset.save()
                messages.success(request, "Success!!!")
                return redirect ('calpage')
            else:
                messages.error(request, "Error in WO!!!")
                return redirect ('calpage')
        
        except Exception as e:
            # Catch-all for any other exceptions
            messages.error(request, f"An unexpected error occurred: {str(e)}")
            return redirect ('calpage')
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
def edit_workbook(request, pk):
    # Fetch the workbook record or return 404 if not found
    workbook = get_object_or_404(Workbook, pk=pk)

    if request.method == 'POST':
        # --- Handle FORM submission ---

        # Basic fields
        workbook.wo_id = request.POST.get('wo_id')
        workbook.asset_id = request.POST.get('asset_id')
        workbook.asset_name = request.POST.get('asset_name')
        workbook.asset_type = request.POST.get('asset_type')
        workbook.make = request.POST.get('make')
        workbook.model = request.POST.get('model')
        workbook.slno = request.POST.get('slno')
        workbook.dept = request.POST.get('dept')
        workbook.reportingDept = request.POST.get('reportingDept')
        workbook.wotype = request.POST.get('wotype')
        workbook.status = request.POST.get('status')
        workbook.reporter = request.POST.get('reporter')
        workbook.loginid = request.POST.get('loginid')
        workbook.eng_id = request.POST.get('eng_id')
        workbook.woapprover = request.POST.get('woapprover')
        workbook.description = request.POST.get('description')
        workbook.parts_description = request.POST.get('parts_description')
        workbook.action = request.POST.get('action')

        # Numeric fields
        workbook.parts_cost = request.POST.get('parts_cost') or None
        workbook.rsndtime = request.POST.get('rsndtime') or None
        workbook.downtime = request.POST.get('downtime') or None

        # DateTime fields
        workbook.wo_date = parse_datetime(request.POST.get('wo_date')) if request.POST.get('wo_date') else None
        workbook.wo_attended = parse_datetime(request.POST.get('wo_attended')) if request.POST.get('wo_attended') else None
        workbook.wo_done = parse_datetime(request.POST.get('wo_done')) if request.POST.get('wo_done') else None

        # Delete existing files if checkbox checked
        if request.POST.get('delete_usersign') and workbook.usersign:
            workbook.usersign.delete()
            workbook.usersign = None
        if request.POST.get('delete_eng_sign') and workbook.eng_sign:
            workbook.eng_sign.delete()
            workbook.eng_sign = None
        if request.POST.get('delete_SR_report') and workbook.SR_report:
            workbook.SR_report.delete()
            workbook.SR_report = None
        if request.POST.get('delete_invoice') and workbook.invoice:
            workbook.invoice.delete()
            workbook.invoice = None

        # Save uploaded files (if new ones were added)
        if 'usersign' in request.FILES:
            workbook.usersign = request.FILES['usersign']
        if 'eng_sign' in request.FILES:
            workbook.eng_sign = request.FILES['eng_sign']
        if 'SR_report' in request.FILES:
            workbook.SR_report = request.FILES['SR_report']
        if 'invoice' in request.FILES:
            workbook.invoice = request.FILES['invoice']

        # Final save
        workbook.save()

        return redirect('index')  # or 'workbook_detail', pk=workbook.pk

    # --- GET method: show form with existing values ---
    return render(request, 'editwo.html', {'workbook': workbook,'sidebar_template':'sidebar.html'})
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////