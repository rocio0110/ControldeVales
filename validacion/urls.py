from django.urls import path
from .views import validacion_qr

urlpatterns = [
    path("validacion/", validacion_qr, name="validacion_qr"),
    
]
