from django.db import models
from catalogos.models import Servicio
from accounts.models import ConductorProfile

from django.utils import timezone

class Consumo(models.Model):
    conductor = models.ForeignKey(ConductorProfile, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    aprobado = models.BooleanField(default=False)
    fecha = models.DateTimeField(default=timezone.now)
