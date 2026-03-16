import json
from django.db import models
from accounts.models import ConductorProfile


class RutaProgramada(models.Model):

    ORIGENES = [
        ("M4D", "M4D"),
        ("M2D", "M2D"),
        ("M6D", "M6D"),
        ("AOD", "AOD"),
        ("TLM", "TLM"),
        ("FUD", "FUD"),
    ]

    DESTINOS = [
        ("AOA", "AOA"),
        ("VEV", "VEV"),
        ("JAV", "JAV"),
        ("CHK", "CHK"),
        ("CBV", "CBV"),
    ]

    DIAS = [
        ("L", "Lunes"),
        ("M", "Martes"),
        ("W", "Miércoles"),
        ("J", "Jueves"),
        ("V", "Viernes"),
        ("S", "Sábado"),
        ("D", "Domingo"),
    ]

    origen = models.CharField(max_length=10, choices=ORIGENES)
    destino = models.CharField(max_length=10, choices=DESTINOS)
    hora_salida = models.TimeField()
    dias_operacion = models.TextField(default="[]")
    conductores_requeridos = models.IntegerField(default=1)
    lugar_vales = models.TextField(blank=True, null=True)   # 👈 NUEVO
    activa = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.hora_salida} | {self.origen} → {self.destino}"

    def set_dias_operacion(self, lista_dias):
        self.dias_operacion = json.dumps(lista_dias)

    def get_dias_operacion(self):
        try:
            return json.loads(self.dias_operacion)
        except:
            return []

    def dias_formateados(self):
        return ",".join(self.get_dias_operacion())
    
    def get_lugares_vales(self):

        if not self.lugar_vales:
            return []

        resultado = []

        items = self.lugar_vales.split(",")

        for item in items:
            lugar = item.split("(")[0]
            cantidad = item.split("(")[1].replace(")", "")
            resultado.append((lugar, cantidad))

        return resultado


class AsignacionRuta(models.Model):
    ruta = models.ForeignKey(
        RutaProgramada,
        on_delete=models.CASCADE,
        related_name="asignaciones"
    )

    conductor_1 = models.ForeignKey(
        ConductorProfile,
        on_delete=models.CASCADE,
        related_name="asignaciones_conductor1"
    )

    conductor_2 = models.ForeignKey(
        ConductorProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asignaciones_conductor2"
    )

    activa = models.BooleanField(default=True)
    fecha_asignacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.ruta} - {self.conductor_1}"
    
