from django.shortcuts import render, redirect, get_object_or_404
from .models import RutaProgramada, AsignacionRuta
from .forms import RutaProgramadaForm, AsignacionRutaForm
from accounts.models import ConductorProfile
import pandas as pd
from django.contrib import messages
from datetime import datetime
from django.db.models import Q
from django.db.models import Prefetch
from .models import AsignacionRuta
from django.utils.dateparse import parse_date


def recarga_nueva(request):

    rutas_existentes = RutaProgramada.objects.all().order_by("hora_salida")

    # FILTRO 24 HORAS
    hora_inicio = request.GET.get("hora_inicio")
    hora_fin = request.GET.get("hora_fin")

    if hora_inicio and hora_fin:
        try:
            hora_inicio_obj = datetime.strptime(hora_inicio, "%H:%M").time()
            hora_fin_obj = datetime.strptime(hora_fin, "%H:%M").time()

            # Caso normal
            if hora_inicio_obj <= hora_fin_obj:
                rutas_existentes = rutas_existentes.filter(
                    hora_salida__range=(hora_inicio_obj, hora_fin_obj)
                )
            else:
                # Caso cruzando medianoche
                rutas_existentes = rutas_existentes.filter(
                    Q(hora_salida__gte=hora_inicio_obj) |
                    Q(hora_salida__lte=hora_fin_obj)
                )

        except ValueError:
            pass

    form = RutaProgramadaForm()
    asignacion_form = AsignacionRutaForm()

    if request.method == "POST":

        #  CREAR RUTA
        if "submit_form" in request.POST:
            form = RutaProgramadaForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Ruta creada correctamente.")
                return redirect("recarga_nueva")

        # IMPORTAR EXCEL
        elif "submit_excel" in request.POST and request.FILES.get("excel_file"):

            excel_file = request.FILES["excel_file"]

            try:
                df = pd.read_excel(excel_file)

                for _, row in df.iterrows():
                    ruta = RutaProgramada(
                        origen=row["origen"],
                        destino=row["destino"],
                        hora_salida=row["hora_salida"],
                        conductores_requeridos=row.get("conductores_requeridos", 1),
                        lugar_vales=row.get("lugar_vales", ""),
                        activa=True,
                    )

                    dias = str(row.get("dias_operacion", "")).split(",")
                    dias = [d.strip() for d in dias if d.strip()]
                    ruta.set_dias_operacion(dias)

                    ruta.save()

                messages.success(request, "Las rutas se importaron correctamente desde el archivo Excel.")
                return redirect("recarga_nueva")

            except Exception as e:
                messages.error(request, f"Error al importar: {e}")
                return redirect("recarga_nueva")

        # ASIGNACIÓN
        elif "submit_asignacion" in request.POST:

            ruta_id = request.POST.get("ruta_id")
            ruta = get_object_or_404(RutaProgramada, id=ruta_id)

            asignacion_form = AsignacionRutaForm(request.POST)

            if asignacion_form.is_valid():
                asignacion = asignacion_form.save(commit=False)
                asignacion.ruta = ruta
                asignacion.save()
                messages.success(request, "Conductores asignados correctamente.")
                return redirect("recarga_nueva")

    return render(request, "recargas/nueva.html", {
        "form": form,
        "asignacion_form": asignacion_form,
        "rutas_existentes": rutas_existentes,
    })
    

    


def recargas_historial(request):

    fecha = request.GET.get("fecha")

    rutas = RutaProgramada.objects.prefetch_related(
        "asignaciones__conductor_1",
        "asignaciones__conductor_2"
    )

    if fecha:
        rutas = rutas.filter(asignaciones__fecha_asignacion=fecha)

    return render(request, "recargas/historial.html", {
        "rutas": rutas,
        "fecha": fecha
    })

def recarga_masiva(request):
    return render(request, "recargas/masiva.html", {})


def recarga_editar(request, recarga_id):

    recarga = get_object_or_404(AsignacionRuta, id=recarga_id)
    conductores = ConductorProfile.objects.all().order_by("clave")

    if request.method == "POST":

        conductor_1_id = request.POST.get("conductor_1_id")
        conductor_2_id = request.POST.get("conductor_2_id")

        #  Validar duplicado
        if conductor_1_id and conductor_2_id:
            if conductor_1_id == conductor_2_id:
                messages.error(request, "No puedes asignar el mismo conductor dos veces.")
                return redirect("recarga_editar", recarga_id=recarga.id)

        # Guardar cambios
        recarga.conductor_1_id = conductor_1_id
        recarga.conductor_2_id = conductor_2_id if conductor_2_id else None
        recarga.save()

        messages.success(request, "Corrida actualizada correctamente.")
        return redirect("recargas_historial")

    return render(request, "recargas/editar.html", {
        "recarga": recarga,
        "conductores": conductores
    })
    
    
def recarga_eliminar(request, recarga_id):
    ruta = get_object_or_404(RutaProgramada, id=recarga_id)

    if request.method == "POST":
        ruta.delete()
        return redirect("recarga_nueva")

    return render(request, "recargas/eliminar.html", {
        "ruta": ruta
    })
    
    
