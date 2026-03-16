# Django básicos
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q

# Python
from datetime import timedelta
from io import BytesIO
import json

# Librerías externas
import qrcode
import openpyxl

# ReportLab (PDF)
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

# Modelos propios
from .models import ConductorProfile, ValeConsumido
from recargas.models import AsignacionRuta

# Formularios
from .forms import (
    UsuarioInternoCreateForm,
    ConductorCreateForm,
    PrimerIngresoForm,
    ConductorEditForm
)

# User model
User = get_user_model()

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

from .models import ConductorProfile, ValeConsumido
from recargas.models import AsignacionRuta
from .forms import (
    UsuarioInternoCreateForm,
    ConductorCreateForm,
    PrimerIngresoForm,
    ConductorEditForm
)

User = get_user_model()

def es_admin(user):
    return user.is_authenticated and user.rol == "admin"
@login_required
@user_passes_test(es_admin)
def dashboard_admin(request):

    total_usuarios = User.objects.count()
    total_conductores = ConductorProfile.objects.count()
    total_vales = ValeConsumido.objects.count()

    return render(request, "dashboards/admin.html", {
        "total_usuarios": total_usuarios,
        "total_conductores": total_conductores,
        "total_vales": total_vales,
    })

def es_preceptor(user):
    return user.is_authenticated and user.rol == "preceptor"


@login_required
@user_passes_test(es_preceptor)
def dashboard_preceptor(request):

    conductores_activos = ConductorProfile.objects.count()

    return render(request, "dashboards/preceptor.html", {
        "conductores_activos": conductores_activos
    })
    
def es_conductor(user):
    return user.is_authenticated and user.rol == "conductor"

def es_comedor(user):
    return user.is_authenticated and user.rol == "comedor"


def es_auditor(user):
    return user.is_authenticated and user.rol == "auditor"

def es_preceptor(user):
    return user.is_authenticated and user.rol == "preceptor"

@login_required
@user_passes_test(es_auditor)
def dashboard_auditor(request):

    hoy = timezone.now().date()

    total_hoy = ValeConsumido.objects.filter(
        fecha__date=hoy
    ).count()

    return render(request, "dashboards/auditor.html", {
        "total_hoy": total_hoy
    })

@login_required
@user_passes_test(es_admin)
def usuarios_list(request):

    usuarios = User.objects.all().order_by("username")

    return render(request, "accounts/usuarios_list.html", {
        "usuarios": usuarios
    })

@login_required
@user_passes_test(es_admin)
def usuarios_nuevo(request):

    if request.method == "POST":
        form = UsuarioInternoCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado correctamente.")
            return redirect("usuarios_list")
    else:
        form = UsuarioInternoCreateForm()

    return render(request, "accounts/conductores_nuevo.html", {
        "form": form
    })
    
@login_required
@user_passes_test(es_admin)
def conductores_list(request):

    conductores = ConductorProfile.objects.select_related("user")

    return render(request, "conductores/list.html", {
        "conductores": conductores
    })    

@login_required
@user_passes_test(es_admin)
def conductores_nuevo(request):

    if request.method == "POST":
        form = ConductorCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Conductor creado correctamente.")
            return redirect("conductores_list")
    else:
        form = ConductorCreateForm()

    return render(request, "accounts/conductores_nuevo.html", {
        "form": form
    })
    
@login_required
@user_passes_test(es_admin)
def conductor_detalle(request, clave):

    conductor = get_object_or_404(ConductorProfile, clave=clave)

    vales = ValeConsumido.objects.filter(
        conductor=conductor
    ).order_by("-fecha")

    return render(request, "conductores/detail.html", {
        "conductor": conductor,
        "vales": vales
    })

@login_required
@user_passes_test(es_admin)
def conductor_editar(request, clave):

    conductor = get_object_or_404(ConductorProfile, clave=clave)

    if request.method == "POST":
        form = ConductorEditForm(request.POST, instance=conductor)
        if form.is_valid():
            form.save()
            messages.success(request, "Conductor actualizado.")
            return redirect("conductores_list")
    else:
        form = ConductorEditForm(instance=conductor)

    return render(request, "accounts/conductor_editar.html", {
        "form": form
    })

@login_required
@user_passes_test(es_admin)
def conductor_eliminar(request, clave):

    conductor = get_object_or_404(ConductorProfile, clave=clave)

    if request.method == "POST":
        conductor.delete()
        messages.success(request, "Conductor eliminado.")
        return redirect("conductores_list")

    return render(request, "conductores/eliminar.html", {
        "conductor": conductor
    })

@login_required
@user_passes_test(es_conductor)
def conductor_qr(request):

    try:
        conductor = request.user.conductor_profile
    except ConductorProfile.DoesNotExist:
        messages.error(request, "No tienes perfil de conductor.")
        return redirect("dashboard_conductor")

    return render(request, "accounts/conductor_qr.html", {
        "conductor": conductor
    })

@login_required
@user_passes_test(es_conductor)
def conductor_qr_png(request):

    try:
        conductor = request.user.conductor_profile
    except ConductorProfile.DoesNotExist:
        return HttpResponse(status=404)

    qr = qrcode.make(conductor.clave)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    return HttpResponse(buffer.getvalue(), content_type="image/png")

@login_required
@user_passes_test(es_auditor)
def auditoria_reportes(request):

    registros = ValeConsumido.objects.select_related("conductor")

    return render(request, "auditoria/reportes.html", {
        "registros": registros
    })

@login_required
@user_passes_test(es_auditor)
def exportar_excel_auditoria(request):

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Auditoria"

    ws.append(["Conductor", "Ruta", "Lugar", "Fecha"])

    for registro in ValeConsumido.objects.all():
        ws.append([
            str(registro.conductor),
            str(registro.ruta),
            registro.lugar,
            registro.fecha.strftime("%Y-%m-%d %H:%M")
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=auditoria.xlsx"

    wb.save(response)
    return response

@login_required
@user_passes_test(es_auditor)
def exportar_pdf_auditoria(request):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph("Reporte de Auditoría", styles["Heading1"]))
    elements.append(Spacer(1, 12))

    data = [["Conductor", "Ruta", "Lugar", "Fecha"]]

    for registro in ValeConsumido.objects.all():
        data.append([
            str(registro.conductor),
            str(registro.ruta),
            registro.lugar,
            registro.fecha.strftime("%Y-%m-%d")
        ])

    table = Table(data)
    table.setStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
    ])

    elements.append(table)
    doc.build(elements)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=auditoria.pdf"
    response.write(buffer.getvalue())

    return response

@login_required
def primer_ingreso(request):

    if request.method == "POST":
        form = PrimerIngresoForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Contraseña actualizada.")
            return redirect("login")
    else:
        form = PrimerIngresoForm(request.user)

    return render(request, "accounts/primer_ingreso.html", {
        "form": form
    })

def login_view(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if user.rol == "admin":
                return redirect("dashboard_admin")
            elif user.rol == "conductor":
                return redirect("dashboard_conductor")
            elif user.rol == "comedor":
                return redirect("dashboard_comedor")
            elif user.rol == "auditor":
                return redirect("dashboard_auditor")

            return redirect("login")

        messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, "accounts/login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
@user_passes_test(es_conductor)
def dashboard_conductor(request):

    try:
        conductor = request.user.conductor_profile
    except ConductorProfile.DoesNotExist:
        messages.error(request, "No tienes perfil de conductor.")
        return redirect("login")

    hoy = timezone.now().date()

    asignacion = AsignacionRuta.objects.filter(
        activa=True
    ).filter(
        Q(conductor_1=conductor) |
        Q(conductor_2=conductor)
    ).select_related("ruta").first()

    ruta = asignacion.ruta if asignacion else None
    vales_disponibles = ruta.get_lugares_vales() if ruta else []

    vales_consumidos_hoy = ValeConsumido.objects.filter(
        conductor=conductor,
        fecha__date=hoy
    )

    return render(request, "dashboards/conductor.html", {
        "conductor": conductor,
        "ruta": ruta,
        "vales_disponibles": vales_disponibles,
        "vales_consumidos_hoy": vales_consumidos_hoy,
        "total_consumidos": vales_consumidos_hoy.count()
    })
    
    
@login_required
@user_passes_test(es_comedor)
def dashboard_comedor(request):

    hoy = timezone.now().date()

    validaciones_hoy = ValeConsumido.objects.filter(
        fecha__date=hoy
    ).count()

    saldo_bajo = ConductorProfile.objects.filter(
        saldo__lt=50
    ).count()

    return render(request, "dashboards/comedor.html", {
        "validaciones_hoy": validaciones_hoy,
        "saldo_bajo": saldo_bajo,
        "rechazadas": 0
    })
    
@login_required
@user_passes_test(es_comedor)
def validacion_comedor(request):

    conductor = None
    ruta = None
    vales = []

    if request.method == "POST":

        clave = request.POST.get("clave")
        descontar = request.POST.get("descontar")

        try:
            conductor = ConductorProfile.objects.get(clave=clave)

            asignacion = AsignacionRuta.objects.filter(
                activa=True
            ).filter(
                Q(conductor_1=conductor) |
                Q(conductor_2=conductor)
            ).select_related("ruta").first()

            if not asignacion:
                messages.error(request, "El conductor no tiene ruta activa.")
                return render(request, "comedor/validacion.html")

            ruta = asignacion.ruta
            vales = ruta.get_lugares_vales()

            if descontar:
                lugar = request.POST.get("lugar")

                ya_consumido = ValeConsumido.objects.filter(
                    conductor=conductor,
                    ruta=ruta,
                    lugar=lugar,
                    fecha__date=timezone.now().date()
                ).exists()

                if ya_consumido:
                    messages.warning(request, "Este vale ya fue usado hoy.")
                else:
                    ValeConsumido.objects.create(
                        conductor=conductor,
                        ruta=ruta,
                        lugar=lugar,
                        validado_por=request.user
                    )
                    messages.success(request, "Vale descontado correctamente.")

        except ConductorProfile.DoesNotExist:
            messages.error(request, "Clave no encontrada.")

    return render(request, "comedor/validacion.html", {
        "conductor": conductor,
        "ruta": ruta,
        "vales": vales
    })
    
from django.shortcuts import render
from django.contrib import messages
from accounts.models import ConductorProfile
from recargas.models import AsignacionRuta, RutaProgramada
from django.utils import timezone

@login_required
@user_passes_test(es_comedor)
def validacion_qr(request):

    resultado = None
    conductor = None
    ruta = None
    servicio = None
    vales_disponibles = []
    ultimo_consumo = None

    servicios = Servicio.objects.all()
    hoy = timezone.now().date()

    if request.method == "POST":

        clave = request.POST.get("clave_manual")
        qr_data = request.POST.get("qr_data")
        servicio_id = request.POST.get("servicio_id")

        # Buscar conductor
        if clave:
            conductor = ConductorProfile.objects.filter(clave=clave).first()

        elif qr_data:
            conductor = ConductorProfile.objects.filter(clave=qr_data).first()

        if not conductor:
            resultado = "qr_invalido"

        else:
            asignacion = AsignacionRuta.objects.filter(
                ruta__activa=True
            ).filter(
                Q(conductor_1=conductor) |
                Q(conductor_2=conductor)
            ).select_related("ruta").first()

            if not asignacion:
                resultado = "denegado"

            else:
                ruta = asignacion.ruta
                vales_ruta = ruta.get_lugares_vales()

                # 🔹 Calcular vales disponibles
                for lugar, cantidad in vales_ruta:

                    cantidad = int(cantidad)

                    consumidos = ValeConsumido.objects.filter(
                        conductor=conductor,
                        ruta=ruta,
                        lugar=lugar,
                        fecha__date=hoy
                    ).count()

                    restantes = cantidad - consumidos

                    vales_disponibles.append({
                        "lugar": lugar,
                        "asignados": cantidad,
                        "consumidos": consumidos,
                        "restantes": restantes
                    })

                # 🔹 Validar servicio seleccionado
                if servicio_id:

                    servicio = Servicio.objects.filter(id=servicio_id).first()

                    if not servicio:
                        resultado = "servicio_invalido"

                    else:
                        nombre_servicio = servicio.nombre

                        for v in vales_disponibles:

                            if v["lugar"] == nombre_servicio:

                                if v["restantes"] <= 0:
                                    resultado = "denegado"
                                else:
                                    ValeConsumido.objects.create(
                                        conductor=conductor,
                                        ruta=ruta,
                                        lugar=nombre_servicio,
                                        validado_por=request.user
                                    )
                                    resultado = "aprobado"

                                break
                        else:
                            resultado = "servicio_invalido"

                ultimo_consumo = ValeConsumido.objects.filter(
                    conductor=conductor
                ).order_by("-fecha").first()

    return render(request, "comedor/validacion.html", {
        "resultado": resultado,
        "conductor": conductor,
        "ruta": ruta,
        "vales_disponibles": vales_disponibles,
        "ultimo_consumo": ultimo_consumo,
        "servicios": servicios,
    })