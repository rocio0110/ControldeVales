from django import forms
from .models import RutaProgramada, AsignacionRuta
from accounts.models import ConductorProfile
from datetime import time


class RutaProgramadaForm(forms.ModelForm):

    dias_operacion = forms.MultipleChoiceField(
        choices=RutaProgramada.DIAS,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Días de operación"
    )

    hora_salida = forms.TimeField(
    widget=forms.TimeInput(
        attrs={
            "type": "time",
            "class": "form-control",
            "style": "padding:8px; border-radius:8px;"
        },
        format="%H:%M"
    ),
    input_formats=["%H:%M"]
)

    class Meta:
        model = RutaProgramada
        fields = [
            "hora_salida",
            "origen",
            "destino",
            "conductores_requeridos",
            "lugar_vales",
            "activa",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Generar horas de 23:59 a 01:00
        horas = []
        for h in [23, 0, 1]:
            for m in range(0, 60):
                horas.append(
                    (f"{h:02d}:{m:02d}", f"{h:02d}:{m:02d}")
                )

        self.fields["hora_salida"].choices = horas

        if self.instance.pk:
            self.fields["dias_operacion"].initial = self.instance.get_dias_operacion()

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Convertir hora string a time
        hora_str = self.cleaned_data.get("hora_salida")
        h, m = map(int, hora_str.split(":"))
        instance.hora_salida = time(h, m)

        dias = self.cleaned_data.get("dias_operacion", [])
        instance.set_dias_operacion(dias)

        if commit:
            instance.save()

        return instance


class AsignacionRutaForm(forms.ModelForm):

    conductor_1 = forms.ModelChoiceField(
        queryset=ConductorProfile.objects.all(),
        label="Conductor 1"
    )

    conductor_2 = forms.ModelChoiceField(
        queryset=ConductorProfile.objects.all(),
        required=False,
        label="Conductor 2"
    )

    class Meta:
        model = AsignacionRuta
        fields = ["conductor_1", "conductor_2", "activa"]

    def clean(self):
        cleaned_data = super().clean()
        c1 = cleaned_data.get("conductor_1")
        c2 = cleaned_data.get("conductor_2")

        if c1 and c2 and c1 == c2:
            raise forms.ValidationError("No puedes asignar el mismo conductor dos veces.")

        return cleaned_data