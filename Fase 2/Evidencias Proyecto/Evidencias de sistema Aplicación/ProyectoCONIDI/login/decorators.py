from django.shortcuts import redirect, render
from functools import wraps


def rol_requerido(roles_permitidos=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            user_role = request.user.tipo_usuario.nombre.lower() if hasattr(request.user, 'tipo_usuario') else None
            roles_permitidos_lower = [r.lower() for r in roles_permitidos]

            if user_role not in roles_permitidos_lower:
                # Mostrar página 403 personalizada
                return render(request, '403.html', status=403)

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def clave_no_temporal(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if getattr(request.user, 'clave_temporal', False):
                # Redirige a la página de cambiar clave temporal
                if request.path != '/cambiar_clave_temporal/':
                    return redirect('cambiar_clave_temporal')
        return view_func(request, *args, **kwargs)
    return wrapper