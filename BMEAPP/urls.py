from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static
#from django.conf.urls.static import static
from django.views.static import serve

from django.conf import settings
from django.views.static import serve


urlpatterns = [
    path('',views.index,name='index'),
    path('logoutuser', views.logoutuser, name='logoutuser'),
    ]

