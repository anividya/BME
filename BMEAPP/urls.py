from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from . import views
from .views import LoginView, WorkbookListView, SaveToken

urlpatterns = [
    # Authentication
    path('register', views.register, name='register'),
    path('logoutuser', views.logoutuser, name='logoutuser'),
    path('check-username/', views.check_username, name='check_username'),

    # Index
    path('', views.index, name='index'),

    # Asset Management
    path('add_asset', views.add_asset, name='add_asset'),
    path('asset_detail/<str:Asset_No>/', views.asset_detail, name='asset_detail'),
    path('asset_data', views.asset_data, name='asset_data'),
    path('asset_quickview/<str:asset_id>/', views.asset_quickview, name='asset_quickview'),
    path('ajax/autocomplete-field/', views.autocomplete_field, name='autocomplete_field'),

    # Work Orders
    path('add_wo', views.add_wo, name='add_wo'),
    path('addwo_ajax/<str:asset_id>/', views.addwo_ajax, name='addwo_ajax'),
    path('view_wo', views.view_wo, name='view_wo'),
    path('attendwo/<str:id>/', views.attendwo, name='attendwo'),
    path('filter_wo', views.filter_wo, name='filter_wo'),
    path('search_woid/', views.search_woid, name='search_woid'),
    path('edit_workbook/<int:pk>/', views.edit_workbook, name='edit_workbook'),
    path('myWork', views.myWork, name='myWork'),
    path('get-documents/', views.get_work_documents, name='get_documents'),
    path('work_data', views.work_data, name='work_data'),

    

    # WO Approval
    path('wo_UserApproval', views.wo_UserApproval, name='wo_UserApproval'),
    path('wouserapprove', views.wouserapprove, name='wouserapprove'),
    path('woGroupAssign', views.woGroupAssign, name='woGroupAssign'),

    # PPM
    path('ppm_Wo', views.ppm_Wo, name='ppm_Wo'),
    path('pmpage', views.pmpage, name='pmpage'),
    path('pmtable_data', views.pmtable_data, name='pmtable_data'),
    path('pmedit', views.pmedit, name='pmedit'),

    # CAL
    path('calpage', views.calpage, name='calpage'),
    path('caltable_data', views.caltable_data, name='caltable_data'),
    path('caledit', views.caledit, name='caledit'),

    # Reports
    path('service-report/<str:wo_id>/', views.generate_service_report, name='service_report'),
    path('monthly-report/', views.monthly_report, name='monthly-report'),

    # Gate Pass
    path('gatepass', views.gatepass, name='gatepass'),
    path('gatepass_print/<str:pass_id>/', views.gatepass_print, name='gatepass_print'),
    path('gatepassform', views.gatepassform, name='gatepassform'),
    path('gatepassAdmin', views.gatepassAdmin, name='gatepassAdmin'),
    path('gatePass_ajax/<str:id>/', views.gatePass_ajax, name='gatePass_ajax'),
    path('gtSendout', views.gtSendout, name='gtSendout'),
    path('gtSend_ajax', views.gtSend_ajax, name='gtSend_ajax'),

    # PR Management
    path('prtable', views.prtable, name='prtable'),
    path('pr_print/<str:prId>/', views.pr_print, name='pr_print'),
    path('pr_approve', views.pr_approve, name='pr_approve'),
    path('pr_adminapr/<str:PR_No>/', views.pr_approve, name='pr_adminapr'),
    path('PPMGeneration', views.PPMGeneration, name='PPMGeneration'),

    # Utilities
    path('utilities', views.utilities, name='utilities'),
    path('check-location/', views.check_location_exists, name='check_location'),
    path('add-department/', views.add_department, name='add_department'),


    # API Endpoints
    path('login/', LoginView.as_view(), name='login'),
    path('save-token/', SaveToken.as_view(), name='save_token'),
]
