from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from login.models import Usuario, Usuario, Rol, Tutor, Profesional
from login.decorators import rol_requerido, clave_no_temporal
from django.shortcuts import get_object_or_404 # <- Asegúrate de que este import esté arriba
from django.db.models import Q
from unidecode import unidecode

from django.contrib.auth.hashers import make_password
import re
import random
import string


# login/views.py

def login_user(request):
    if request.method == "POST":
        # Obtenemos el RUT y lo convertimos a mayúsculas INMEDIATAMENTE
        rut = request.POST.get('rut', '').upper() # <-- CAMBIO CLAVE
        password = request.POST.get('password')

        # Ahora, 'authenticate' siempre recibirá el RUT con la 'K' en mayúscula
        user = authenticate(request, username=rut, password=password)

        if user is not None:
            login(request, user)
            if getattr(user, 'clave_temporal', False):
                return redirect('cambiar_clave_temporal')
            return redirect('home')
        else:
            messages.error(request, "RUT o contraseña incorrectos")

    return render(request, 'authentication/login.html')


@login_required
@clave_no_temporal
@rol_requerido(['Administrador', 'Profesional'])
def crear_usuario(request):
    current_user_rol = request.user.rol.nombre_rol.lower()
    
    contexto = {
        'roles_para_crear': Rol.objects.none(),
        'tutores_para_activar': Tutor.objects.none(),
        'especialidad_choices': Profesional.ESPECIALIDAD_CHOICES
    }

    if current_user_rol == 'administrador':
        contexto['roles_para_crear'] = Rol.objects.filter(nombre_rol__in=['Administrador', 'Profesional'])
        contexto['tutores_para_activar'] = Tutor.objects.filter(usuario__isnull=True)
    elif current_user_rol == 'profesional':
        contexto['tutores_para_activar'] = Tutor.objects.filter(usuario__isnull=True)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create_new':
            rut = request.POST.get('rut')
            nombre = request.POST.get('nombre_completo')
            email = request.POST.get('email')
            rol_id = request.POST.get('rol_id')
            especialidad = request.POST.get('especialidad')
            nueva_clave = request.POST.get('nueva_clave')

            has_error = False
            # --- VALIDACIÓN DE RUT AÑADIDA ---
            if not validar_rut(rut):
                messages.error(request, f"El RUT '{rut}' no es válido.")
                has_error = True
            # ------------------------------------
            elif Usuario.objects.filter(rut=rut).exists() or Profesional.objects.filter(rut=rut).exists() or Tutor.objects.filter(rut=rut).exists():
                messages.error(request, f"El RUT {rut} ya está registrado en el sistema.")
                has_error = True

            if nueva_clave != request.POST.get('confirmar_clave'):
                messages.error(request, "Las contraseñas no coinciden.")
                has_error = True

            if has_error:
                contexto['form_data'] = request.POST
                return render(request, 'authentication/crear_usuario.html', contexto)
            
            try:
                rol_obj = Rol.objects.get(id=rol_id)
                user = Usuario.objects.create_user(
                    rut=rut, email=email, nombre_completo=nombre,
                    rol=rol_obj, password=nueva_clave, clave_temporal=False
                )
                if rol_obj.nombre_rol == 'Profesional':
                    Profesional.objects.create(rut=rut, nombre_completo=nombre, email=email, usuario=user, especialidad=especialidad)
                
                messages.success(request, f"Usuario '{nombre}' creado con éxito.")
            except Exception as e:
                messages.error(request, f"Ocurrió un error al guardar el usuario: {e}")


        # --- Flujo 2: Activación de cuenta para Tutores existentes ---
        elif action == 'activate_tutor':
            tutor_rut = request.POST.get('tutor_rut')
            try:
                tutor = Tutor.objects.get(rut=tutor_rut, usuario__isnull=True)
                rol_tutor = Rol.objects.get(nombre_rol='Tutor')
                
                clave_temp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                
                user = Usuario.objects.create_user(
                    rut=tutor.rut,
                    email=tutor.email,
                    nombre_completo=tutor.nombre_completo,
                    rol=rol_tutor,
                    password=clave_temp,
                    clave_temporal=True
                )
                
                tutor.usuario = user
                tutor.save()
                
                messages.success(request, f"Cuenta para '{tutor.nombre_completo}' activada. Contraseña temporal: {clave_temp}")

            except Tutor.DoesNotExist:
                messages.error(request, "El tutor seleccionado no existe o ya tiene una cuenta.")
            except Rol.DoesNotExist:
                messages.error(request, "El rol 'Tutor' no existe. Ejecuta el script para poblar datos.")
        
        return redirect('crear_usuario')

    # --- Lógica para la petición GET (no cambia) ---
    contexto = {
        'roles_para_crear': Rol.objects.none(),
        'tutores_para_activar': Tutor.objects.none(),
        'especialidad_choices': Profesional.ESPECIALIDAD_CHOICES,
    }
    
    if current_user_rol == 'administrador':
        contexto['roles_para_crear'] = Rol.objects.filter(nombre_rol__in=['Administrador', 'Profesional'])
        contexto['tutores_para_activar'] = Tutor.objects.filter(usuario__isnull=True)
    
    elif current_user_rol == 'profesional':
        contexto['tutores_para_activar'] = Tutor.objects.filter(usuario__isnull=True)

    return render(request, 'authentication/crear_usuario.html', contexto)

def validar_rut(rut):
    rut = rut.upper().replace(".", "").replace("-", "")
    if not re.match(r'^\d{7,8}[0-9K]$', rut):
        return False
    cuerpo = rut[:-1]
    dv = rut[-1]
    
    suma = 0
    multiplo = 2
    for c in reversed(cuerpo):
        suma += int(c) * multiplo
        multiplo = 2 if multiplo == 7 else multiplo + 1


    dv_calculado = 11 - (suma % 11)
    if dv_calculado == 11:
        dv_calculado = '0'
    elif dv_calculado == 10:
        dv_calculado = 'K'
    else:
        dv_calculado = str(dv_calculado)
        
    return dv_calculado == dv


@login_required
@clave_no_temporal
def home(request):
    return render(request, 'home.html')

def logout_user(request):
    logout(request)
    return redirect('home')

@login_required
@clave_no_temporal
def cambiar_clave(request):
    if request.method == 'POST':
        clave_actual = request.POST.get('clave_actual')
        nueva_clave = request.POST.get('nueva_clave')
        confirmar_clave = request.POST.get('confirmar_clave')

        if not (clave_actual and nueva_clave and confirmar_clave):
            messages.error(request, "Todos los campos son obligatorios.")
        elif not request.user.check_password(clave_actual):
            messages.error(request, "La contraseña actual no es correcta.")
        elif nueva_clave != confirmar_clave:
            messages.error(request, "Las contraseñas no coinciden.")
        else:
            request.user.set_password(nueva_clave)
            request.user.save()
            messages.success(request, "Contraseña cambiada correctamente.")
            return redirect('home')

    return render(request, 'authentication/cambiar_clave.html')


@clave_no_temporal
@login_required
def cambiar_clave_temporal(request):
    if request.method == 'POST':
        nueva_clave = request.POST.get('nueva_clave')
        confirmar_clave = request.POST.get('confirmar_clave')

        if not (nueva_clave and confirmar_clave):
            messages.error(request, "Todos los campos son obligatorios.")
        elif nueva_clave != confirmar_clave:
            messages.error(request, "Las contraseñas no coinciden.")
        else:
            request.user.set_password(nueva_clave)
            request.user.clave_temporal = False  # Ya no es clave temporal
            request.user.save()
            messages.success(request, "Contraseña cambiada correctamente.")
            return redirect('home')

    return render(request, 'authentication/cambiar_clave_temporal.html')


@login_required
#@rol_requerido(['Administrador']) 
def listar_usuarios(request):
    user = request.user
    rol_usuario_actual = user.rol.nombre_rol.lower()

    # --- NUEVO: Capturamos los datos del formulario de filtros ---
    nombre_query = request.GET.get('nombre', '')
    rut_query = request.GET.get('rut', '')

    # --- Obtener la lista base según el rol ---
    lista_usuarios = Usuario.objects.none()
    if rol_usuario_actual == 'administrador':
        # Admin ve a todos menos a sí mismo (opcional)
        lista_usuarios = Usuario.objects.select_related('rol').exclude(pk=user.pk)
    elif rol_usuario_actual == 'profesional':
        # Profesional SOLO ve a los Tutores
        lista_usuarios = Usuario.objects.select_related('rol').filter(rol__nombre_rol__iexact='tutor')

    # --- Aplicamos los filtros sobre la lista base ---
    if nombre_query:
        nombre_query_norm = unidecode(nombre_query).lower()
        lista_usuarios = lista_usuarios.filter(
            nombre_completo_norm__icontains=nombre_query_norm
            # Si hubieran campos separados nombre/apellido en Usuario, se añadiria Q() para ellos aquí
        )

    if rut_query:
        # Filtramos por RUT 
        lista_usuarios = lista_usuarios.filter(rut__icontains=rut_query)

    # --- Enviamos el contexto ---
    contexto = {
        # Ordenamos DESPUÉS de filtrar
        'usuarios': lista_usuarios.order_by('nombre_completo'),
        'rol_usuario': rol_usuario_actual, # Pasa el rol para lógica en template si es necesario
        # Pasamos los valores de búsqueda de vuelta para rellenar el formulario
        'nombre_query': nombre_query,
        'rut_query': rut_query,
    }
    return render(request, 'authentication/listar_usuarios.html', contexto)


@login_required
@rol_requerido(['Administrador'])
def editar_usuario(request, pk):
    # Usamos get_object_or_404 para obtener el usuario o mostrar un error 404 si no existe
    usuario = get_object_or_404(Usuario, pk=pk)
    roles = Rol.objects.all()

    if request.method == 'POST':
        # Obtenemos los datos del formulario enviado
        usuario.nombre_completo = request.POST.get('nombre_completo')
        usuario.email = request.POST.get('email')
        rol_id = request.POST.get('rol')
        usuario.rol = Rol.objects.get(id=rol_id)
        
        # Para los checkboxes, si no están marcados no se envían en el POST
        usuario.activo = 'activo' in request.POST

        usuario.save()
        messages.success(request, f'El usuario {usuario.nombre_completo} ha sido actualizado correctamente.')
        return redirect('listar_usuarios')

    # Si el método es GET, simplemente mostramos el formulario con los datos del usuario
    contexto = {
        'usuario': usuario,
        'roles': roles,
    }
    return render(request, 'authentication/editar_usuario.html', contexto)


@login_required
@rol_requerido(['Administrador'])
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # Si el formulario de confirmación es enviado...
    if request.method == 'POST':
        nombre_usuario = usuario.nombre_completo
        usuario.delete()
        messages.success(request, f'El usuario {nombre_usuario} ha sido eliminado permanentemente.')
        return redirect('listar_usuarios')
        
    # Si se accede a la URL por primera vez (GET), muestra la página de confirmación
    contexto = {
        'usuario': usuario
    }
    return render(request, 'authentication/eliminar_usuario.html', contexto)

