from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from login.models import Usuario, TipoUsuario
from login.decorators import rol_requerido, clave_no_temporal

from django.contrib.auth.hashers import make_password
import re
import random
import string


def login_user(request):
    if request.method == "POST":
        rut = request.POST.get('rut')
        password = request.POST.get('password')

        user = authenticate(request, username=rut, password=password)

        if user is not None:
            login(request, user)
            if getattr(user, 'clave_temporal', False):
                return redirect('cambiar_clave_temporal')
            return redirect('home')
        else:
            messages.error(request, "RUT o contraseña incorrectos")

    return render(request, 'authentication/login.html')


@clave_no_temporal
@login_required
@rol_requerido(['Administrador', 'Profesional'])
def crear_usuario(request):
    tipos = TipoUsuario.objects.all()
    user_type_allowed = ['Administrador', 'Profesional'] if request.user.tipo_usuario.nombre.lower() == 'administrador' else ['Tutor']

    tipos = tipos.filter(nombre__in=user_type_allowed)

    if request.method == 'POST':
        rut = request.POST.get('rut')
        nombre_completo = request.POST.get('nombre_completo')
        tipo_id = request.POST.get('tipo_usuario')

        if not (rut and nombre_completo and tipo_id):
            messages.error(request, "Todos los campos son obligatorios.")
        elif not validar_rut(rut):
            messages.error(request, "El RUT ingresado no es válido.")
        else:
            tipo = TipoUsuario.objects.get(id=tipo_id)

            usuario, creado = Usuario.objects.get_or_create(
                rut=rut,
                defaults={'nombre_completo': nombre_completo, 'tipo_usuario': tipo}
            )

            if creado:
                # Si el creador es profesional y crea un tutor, generar clave automática
                if request.user.tipo_usuario.nombre.lower() == 'profesional' and tipo.nombre.lower() == 'tutor':
                    codigo_temporal = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                    usuario.set_password(codigo_temporal)
                    usuario.clave_temporal = True  # <--- Aquí marcas que es clave temporal

                    usuario.save()
                    messages.success(request, f"Tutor creado correctamente. Código de acceso: {codigo_temporal}")
                else:
                    clave = request.POST.get('clave')
                    usuario.set_password(clave)
                    usuario.save()
                    messages.success(request, f"Usuario {nombre_completo} creado correctamente.")

                return redirect('crear_usuario')
            else:
                messages.error(request, "El usuario con ese RUT ya existe.")

    return render(request, 'authentication/crear_usuario.html', {'tipos': tipos})


def validar_rut(rut):
    rut = rut.replace(".", "").replace("-", "").upper()
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

@clave_no_temporal
@login_required
def home(request):
    # Determinar si el usuario logeado es admin
    es_admin = False
    if request.user.is_authenticated and request.user.tipo_usuario.nombre.lower() == 'administrador':
        es_admin = True

    return render(request, 'home.html', {'es_admin': es_admin})

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