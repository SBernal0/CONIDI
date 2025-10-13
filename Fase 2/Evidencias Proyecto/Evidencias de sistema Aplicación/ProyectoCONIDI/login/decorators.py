# login/decorators.py
from django.shortcuts import redirect, render
from functools import wraps

def rol_requerido(roles_permitidos=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            # --- LA LÍNEA CLAVE QUE CAMBIÓ ---
            # Ahora accedemos a través del nuevo campo 'rol' y su atributo 'nombre_rol'
            user_role = request.user.rol.nombre_rol if hasattr(request.user, 'rol') else None
            
            # Convertimos a minúsculas para una comparación sin errores
            roles_permitidos_lower = [r.lower() for r in roles_permitidos]

            if not user_role or user_role.lower() not in roles_permitidos_lower:
                return render(request, '403.html', status=403)

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# Este decorador depende del campo 'clave_temporal' que debemos volver a añadir
def clave_no_temporal(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            # Asumimos que volveremos a añadir 'clave_temporal' al modelo Usuario
            if getattr(request.user, 'clave_temporal', False):
                if request.path != '/cambiar_clave_temporal/': # Evita un bucle de redirección
                    return redirect('cambiar_clave_temporal')
        return view_func(request, *args, **kwargs)
    return wrapper