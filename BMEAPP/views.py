from django.shortcuts import render

# Create your views here.
def index(request):
    sidebar_template = 'sidebar.html'
    return render(request, 'dashboard.html',{'sidebar_template': sidebar_template})