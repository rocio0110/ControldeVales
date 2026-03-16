from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from catalogos.models import Servicio
from accounts.models import ConductorProfile
from .models import Consumo
from django.db import transaction
from django.utils import timezone

@login_required
@role_required(["admin", "comedor"])
def validacion_qr(request):
    servicios = Servicio.objects.filter(activo=True)

    resultado = None
    conductor = None
    servicio = None

    saldo_antes = None
    saldo_despues = None
    ultimo_consumo = None

    if request.method == "POST":
        qr_data = request.POST.get("qr_data", "").strip()
        servicio_id = request.POST.get("servicio_id")

        # 1) Validar QR
        try:
            conductor_id = int(qr_data.replace("CONDUCTOR:", "").strip())
            conductor = ConductorProfile.objects.get(id=conductor_id, activo=True)
        except:
            resultado = "qr_invalido"
            return render(request, "validacion/scan.html", {
                "servicios": servicios,
                "resultado": resultado
            })

        # 2) Validar servicio
        try:
            servicio = Servicio.objects.get(id=servicio_id, activo=True)
        except:
            resultado = "servicio_invalido"
            return render(request, "validacion/scan.html", {
                "servicios": servicios,
                "resultado": resultado
            })

        saldo_antes = conductor.saldo

        # 3) Último consumo (info)
        ultimo_consumo = Consumo.objects.filter(conductor=conductor).order_by("-fecha").first()

        # 4) Validar saldo
        if conductor.saldo < servicio.precio:
            Consumo.objects.create(
                conductor=conductor,
                servicio=servicio,
                monto=servicio.precio,
                aprobado=False,
                fecha=timezone.now()
            )

            resultado = "denegado"
            saldo_despues = conductor.saldo

            return render(request, "validacion/scan.html", {
                "servicios": servicios,
                "resultado": resultado,
                "conductor": conductor,
                "servicio": servicio,
                "saldo_antes": saldo_antes,
                "saldo_despues": saldo_despues,
                "ultimo_consumo": ultimo_consumo,
            })

        # 5) Aplicar consumo
        with transaction.atomic():
            conductor.saldo -= servicio.precio
            conductor.save()

            Consumo.objects.create(
                conductor=conductor,
                servicio=servicio,
                monto=servicio.precio,
                aprobado=True,
                fecha=timezone.now()
            )

        resultado = "aprobado"
        saldo_despues = conductor.saldo

        return render(request, "validacion/scan.html", {
            "servicios": servicios,
            "resultado": resultado,
            "conductor": conductor,
            "servicio": servicio,
            "saldo_antes": saldo_antes,
            "saldo_despues": saldo_despues,
            "ultimo_consumo": ultimo_consumo,
        })

    return render(request, "validacion/scan.html", {"servicios": servicios})
