from django.shortcuts import redirect
from django.contrib import messages

def role_required(roles=[]):
    def decorator(view_func):
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")

            if request.user.rol not in roles:
                messages.error(request, "No tienes permisos para acceder a esta sección.")
                return redirect("home")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
