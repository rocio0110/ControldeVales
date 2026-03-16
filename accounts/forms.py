from django import forms
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import ConductorProfile
from django import forms
from .models import ConductorProfile
from django import forms

class MovimientoSaldoForm(forms.Form):
    monto = forms.DecimalField(max_digits=10, decimal_places=2)
    
class ConductorEditForm(forms.ModelForm):
    class Meta:
        model = ConductorProfile
        fields = ["clave", "nombre", "apellido_paterno", "apellido_materno", "marca"]

User = get_user_model()


class UsuarioInternoCreateForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Contraseña temporal"
    )

    class Meta:
        model = User
        fields = ["username", "email", "rol", "password"]

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop("request_user", None)
        super().__init__(*args, **kwargs)

        # Si NO es superuser, no puede crear admins
        if self.request_user and not self.request_user.is_superuser:
            self.fields["rol"].choices = [
                ("preceptor", "Preceptor"),
                ("comedor", "Comedor"),
                ("conductor", "Conductor"),
                ("auditor", "auditor"),
            ]

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya existe.")

        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip()

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        # FORZAMOS primer ingreso
        user.primer_ingreso = True

        if commit:
            user.save()

            # Enviar correo automático
            self.enviar_correo(user, self.cleaned_data["password"])

        return user

    def enviar_correo(self, user, password):
        asunto = "Acceso al sistema OPERACIONES ADO"
        mensaje = f"""
Hola {user.username},

Se ha creado tu cuenta en el sistema.

Usuario: {user.username}
Contraseña temporal: {password}
Rol: {user.get_rol_display()}

⚠️ IMPORTANTE:
Al iniciar sesión por primera vez, el sistema te pedirá cambiar tu contraseña.

Saludos.
        """

        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )


# ---------------------------------
# FORM PARA CONDUCTORES
# ---------------------------------
class ConductorCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=False)

    clave = forms.CharField(max_length=20)
    nombre = forms.CharField(max_length=100)
    apellido_paterno = forms.CharField(max_length=100)
    apellido_materno = forms.CharField(max_length=100, required=False)
    marca = forms.ChoiceField(choices=ConductorProfile.Marca.choices)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.rol = "conductor"
        user.primer_ingreso = True

        if commit:
            user.save()

            ConductorProfile.objects.create(
                user=user,
                clave=self.cleaned_data["clave"],
                nombre=self.cleaned_data["nombre"],
                apellido_paterno=self.cleaned_data["apellido_paterno"],
                apellido_materno=self.cleaned_data.get("apellido_materno", ""),
                marca=self.cleaned_data["marca"],
            )

        return user
    
    
    # ---------------------------------
# FORM PARA PRIMER INGRESO (CAMBIO DE CONTRASEÑA)
# ---------------------------------
class PrimerIngresoForm(forms.Form):
    password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned_data

    def save(self):
        password = self.cleaned_data["password1"]
        self.user.set_password(password)
        self.user.save()
        return self.user
