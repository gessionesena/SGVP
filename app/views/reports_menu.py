from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url='login')
def reports_menu(request):
    return render(request, 'reports_menu.html')
