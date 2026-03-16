
def redireccion_por_rol(user):
    if user.is_superuser:
        return "dashboard_admin"

    if user.rol == "admin":
        return "dashboard_admin"
    if user.rol == "preceptor":
        return "dashboard_preceptor"
    if user.rol == "soporte":
        return "dashboard_soporte"
    if user.rol == "conductor":
        return "dashboard_auditor"
    if user.rol == "auditor":
        return "dashboard_auditor"

    return "home"
