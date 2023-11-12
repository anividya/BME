from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.forms import formset_factory
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from BMEAPP.decorators import allowed_users
from django.http import HttpResponseRedirect
from django.urls import reverse

def loginpage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password = password)

        if user is not None:
            login(request,user)
            return render(request, 'index.html')

        else:
            messages.error(request, 'Username or Password incorrect')
            return render(request, 'login.html')
    
    else:
        return render(request, "login.html")
# ====================================================================
def logoutuser(request):
    logout(request)
    return redirect('login/?next=/')
# ====================================================================   

# Create your views here.
@login_required(login_url="/login/")
def index(request):
    sidebar_template = 'sidebar.html'
    return render(request, 'dashboard.html',{'sidebar_template': sidebar_template})