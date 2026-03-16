from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver   
from django.conf import settings
from django.db import models
# ======================================
# USER PERSONALIZADO
# ======================================

class User(AbstractUser):

    class Roles(models.TextChoices):
        ADMIN = "admin", "Administrador"
        PRECEPTOR = "preceptor", "Preceptor"
        CONDUCTOR = "conductor", "Conductor"
        COMEDOR = "comedor", "Comedor"
        AUDITOR = "auditor", "Auditor"

    rol = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.CONDUCTOR
    )

    primer_ingreso = models.BooleanField(default=True)
    acepto_tyc = models.BooleanField(default=False)

    def es_admin(self):
        return self.is_superuser or self.rol == self.Roles.ADMIN


# ======================================
# PERFIL CONDUCTOR
# ======================================

class ConductorProfile(models.Model):

    class Marca(models.TextChoices):
        PL = "PL", "PL"
        GL = "GL", "GL"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="conductor_profile"
    )

    clave = models.CharField(
        max_length=20,
        unique=True,
        db_index=True
    )

    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)

    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    marca = models.CharField(max_length=2, choices=Marca.choices)

    def __str__(self):
        return f"{self.clave} - {self.nombre} {self.apellido_paterno}"

    # Método seguro para modificar saldo
    def aplicar_movimiento(self, tipo, monto, usuario):

        with transaction.atomic():

            saldo_anterior = self.saldo

            if tipo == "consumo" and monto > self.saldo:
                raise ValueError("Saldo insuficiente")

            if tipo == "recarga":
                self.saldo += monto

            elif tipo == "consumo":
                self.saldo -= monto

            elif tipo == "ajuste":
                self.saldo = monto

            self.save()

            MovimientoSaldo.objects.create(
                conductor=self,
                tipo=tipo,
                monto=monto,
                saldo_anterior=saldo_anterior,
                saldo_nuevo=self.saldo,
                creado_por=usuario
            )


# ======================================
# HISTORIAL FINANCIERO
# ======================================

class MovimientoSaldo(models.Model):

    class Tipo(models.TextChoices):
        RECARGA = "recarga", "Recarga"
        CONSUMO = "consumo", "Consumo"
        AJUSTE = "ajuste", "Ajuste"

    conductor = models.ForeignKey(
        ConductorProfile,
        on_delete=models.CASCADE,
        related_name="movimientos"
    )

    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    saldo_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_nuevo = models.DecimalField(max_digits=10, decimal_places=2)

    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimientos_creados"
    )

    fecha = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.tipo} - {self.conductor.clave} - ${self.monto}"


# ======================================
# VALES CONSUMIDOS (COMEDOR)
# ======================================

from django.conf import settings
from django.db import models

class ValeConsumido(models.Model):

    conductor = models.ForeignKey(
        "accounts.ConductorProfile",
        on_delete=models.CASCADE,
        related_name="vales_consumidos"
    )

    ruta = models.ForeignKey(
        "recargas.RutaProgramada",  # ← AQUI VA recargas
        on_delete=models.CASCADE,
        related_name="vales_consumidos"
    )

    lugar = models.CharField(max_length=100)

    fecha = models.DateTimeField(auto_now_add=True)

    validado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.conductor.clave} - {self.lugar}"
    
# ======================================
# SEÑAL PARA SUPERUSER
# ======================================

@receiver(post_save, sender=User)
def asignar_rol_admin_a_superuser(sender, instance, **kwargs):
    if instance.is_superuser and instance.rol != User.Roles.ADMIN:
        User.objects.filter(pk=instance.pk).update(rol=User.Roles.ADMIN)