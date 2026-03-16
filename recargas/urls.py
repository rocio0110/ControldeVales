from django.urls import path
from . import views

urlpatterns = [
    path("recargas/nueva/", views.recarga_nueva, name="recarga_nueva"),
    path("recargas/historial/", views.recargas_historial, name="recargas_historial"),
    path("recargas/masiva/", views.recarga_masiva, name="recarga_masiva"),
    path("recargas/<int:recarga_id>/editar/", views.recarga_editar, name="recarga_editar"),
    path("recargas/<int:recarga_id>/eliminar/", views.recarga_eliminar, name="recarga_eliminar"),
    
]