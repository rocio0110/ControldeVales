from django.urls import path
from . import views 


urlpatterns = [
    path("logout/", views.logout_view, name="logout"),

    path("login/", views.login_view, name="login"),
    path("primer-ingreso/", views.primer_ingreso, name="primer_ingreso"),

    path("dashboard/admin/", views.dashboard_admin, name="dashboard_admin"),
    path("dashboard/preceptor/", views.dashboard_preceptor, name="dashboard_preceptor"),
    path("dashboard/comedor/", views.dashboard_comedor, name="dashboard_comedor"),
    path("dashboard/conductor/", views.dashboard_conductor, name="dashboard_conductor"),
    path("dashboard/auditor/", views.dashboard_auditor, name="dashboard_auditor"),


    path("usuarios/", views.usuarios_list, name="usuarios_list"),
    path("usuarios/nuevo/", views.usuarios_nuevo, name="usuarios_nuevo"),

    path("conductores/", views.conductores_list, name="conductores_list"),
    path("conductores/nuevo/", views.conductores_nuevo, name="conductores_nuevo"),

    path("conductor/qr/", views.conductor_qr, name="conductor_qr"),
    path("conductor/qr/png/", views.conductor_qr_png, name="conductor_qr_png"),
    

    path("conductores/<str:clave>/", views.conductor_detalle, name="conductor_detalle"),
    path("conductores/<str:clave>/editar/", views.conductor_editar, name="conductor_editar"),
    path("conductores/<str:clave>/eliminar/", views.conductor_eliminar, name="conductor_eliminar"),
    
    path("auditoria/reportes/", views.auditoria_reportes, name="auditoria_reportes"),
    path("auditoria/exportar-excel/", views.exportar_excel_auditoria, name="auditoria_exportar_excel"),
    path("auditoria/exportar-pdf/", views.exportar_pdf_auditoria, name="auditoria_exportar_pdf"),


    path("validacion/", views.validacion_comedor, name="validacion_comedor"),
]
