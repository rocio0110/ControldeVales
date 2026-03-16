from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    # redirección por rol
    if request.user.rol == "admin":
        return redirect("dashboard_admin")
    if request.user.rol == "preceptor":
        return redirect("dashboard_preceptor")
    if request.user.rol == "conductor":
        return redirect("dashboard_conductor")
    return redirect("dashboard_comedor")


@login_required
def dashboard_admin(request):
    return render(request, "dashboards/admin.html")


@login_required
def dashboard_preceptor(request):
    return render(request, "dashboards/preceptor.html")


@login_required
def dashboard_conductor(request):
    return render(request, "dashboards/conductor.html")


@login_required
def dashboard_comedor(request):
    return render(request, "dashboards/comedor.html")
