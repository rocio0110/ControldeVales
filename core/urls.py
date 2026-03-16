from django.contrib import admin
from django.urls import path, include
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", home, name="home"),

    path("dashboard-admin/", dashboard_admin, name="dashboard_admin"),
    path("dashboard-preceptor/", dashboard_preceptor, name="dashboard_preceptor"),
    path("dashboard-conductor/", dashboard_conductor, name="dashboard_conductor"),
    path("dashboard-comedor/", dashboard_comedor, name="dashboard_comedor"),

    path("", include("accounts.urls")),
    path("", include("recargas.urls")),
    path("", include("validacion.urls")),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)