from django.shortcuts import render, get_object_or_404, redirect   
from datetime import date, timedelta
from .models import Nino
from django.contrib.auth.decorators import login_required
from login.models import Tutor # <- Importamos el modelo Tutor
from django.core.exceptions import PermissionDenied # <-- AÑADE ESTE IMPORT
from django.contrib import messages
from .models import Control, PeriodoControl
from login.decorators import rol_requerido
from django.core.management import call_command
from simple_history.admin import SimpleHistoryAdmin


@login_required
def controles(request, nino_rut):
    # Obtenemos el niño que se está pidiendo en la URL
    nino = get_object_or_404(Nino, pk=nino_rut)
    user = request.user
    
    # --- NUEVA VERIFICACIÓN DE PERMISOS ---
    # Si el usuario es un tutor, verificamos que el niño le pertenezca
    if user.rol.nombre_rol.lower() == 'tutor':
        # Chequeamos si el niño solicitado está en la lista de niños del tutor.
        # user.perfil_tutor.ninos.filter(pk=nino.pk) intenta encontrar al niño dentro de la lista del tutor.
        # .exists() devuelve True si lo encuentra, False si no.
        if not user.perfil_tutor.ninos.filter(pk=nino.pk).exists():
            # Si el niño no está en su lista, lanzamos un error de Permiso Denegado (403 Forbidden).
            raise PermissionDenied
    
    # Si el usuario es Admin/Profesional, o si es un Tutor y la verificación anterior pasó,
    # la vista continúa ejecutándose normalmente.
    
    lista_controles = nino.controles.all().order_by('fecha_control_programada')

    contexto = {
        "nino": nino,
        "controles": lista_controles
    }
    return render(request, 'control/controles.html', context=contexto)

@login_required
def listar_ninos(request):
    user = request.user
    rol_usuario = user.rol.nombre_rol.lower()
    
    lista_ninos = Nino.objects.none() # Por defecto, una lista vacía

    if rol_usuario in ['administrador', 'profesional']:
        # Si es admin o profesional, muestra todos los niños
        lista_ninos = Nino.objects.all().order_by('nombre', 'ap_paterno')
    
    elif rol_usuario == 'tutor':
        # Si es tutor, intenta obtener su perfil y muestra solo sus niños asignados
        try:
            # Usamos el 'related_name' que definimos en el OneToOneField
            lista_ninos = user.perfil_tutor.ninos.all().order_by('nombre', 'ap_paterno')
        except Tutor.DoesNotExist:
            # En caso de que un usuario con rol 'Tutor' no tenga un perfil Tutor asociado (poco probable)
            lista_ninos = Nino.objects.none()

    contexto = {
        'ninos': lista_ninos
    }
    return render(request, 'control/listar_ninos.html', contexto)

@login_required
@rol_requerido(['Administrador', 'Profesional'])
def registrar_control(request, control_id):
    control = get_object_or_404(Control, pk=control_id)
    nino = control.nino

    if request.method == 'POST':
        # --- Recolectamos TODOS los datos del formulario ---
        control.fecha_realizacion_control = request.POST.get('fecha_realizacion')
        
        # Datos antropométricos
        control.pesokg = float(request.POST.get('pesokg'))
        control.talla_cm = float(request.POST.get('talla_cm'))
        control.pc_cm = request.POST.get('pc_cm') if request.POST.get('pc_cm') else None
        
        # Cálculo automático del IMC
        if control.talla_cm > 0:
            talla_m = control.talla_cm / 100
            control.imc = round(control.pesokg / (talla_m ** 2), 2)
        
        # Calificaciones
        control.calificacion_nutricional = request.POST.get('calificacion_nutricional')
        control.calificacion_estatural = request.POST.get('calificacion_estatural')
        control.calificacion_pce = request.POST.get('calificacion_pce')
        control.dig_pa = request.POST.get('dig_pa')
        
        # Textos largos
        control.diag_des_integral = request.POST.get('diag_des_integral')
        control.obs_desarrollo_integral = request.POST.get('obs_desarrollo_integral')
        control.observaciones = request.POST.get('observaciones')
        control.indicaciones = request.POST.get('indicaciones')
        
        # Checkboxes (si están marcados, existen en request.POST)
        control.derivacion = 'derivacion' in request.POST
        control.consulta_dental_realizada = 'consulta_dental_realizada' in request.POST
        control.derivacion_dentista = 'derivacion_dentista' in request.POST

        # Estado y profesional
        control.estado_control = 'Realizado'
        try:
            control.profesional = request.user.perfil_profesional
        except:
            pass
        
        control.save()
        messages.success(request, f'El "{control.nombre_control}" ha sido registrado exitosamente.')
        return redirect('controles', nino_rut=nino.rut_nino)

    # --- Preparamos el contexto para la petición GET ---
    contexto = {
        'control': control,
        'nino': nino,
        # Pasamos las opciones de los 'choices' a la plantilla para los menús desplegables
        'estatural_choices': Control.CALIFICACION_ESTATURAL_CHOICES,
        'pce_choices': Control.CALIFICACION_PCE_CHOICES,
        'pa_choices': Control.DIG_PA_CHOICES,
    }
    return render(request, 'control/registrar_control.html', contexto)


@login_required
def ver_control(request, control_id):
    control = get_object_or_404(Control, pk=control_id)
    nino = control.nino
    user = request.user

    # --- Verificación de Seguridad ---
    # Si el usuario es un tutor, nos aseguramos de que el niño le pertenezca
    if user.rol.nombre_rol.lower() == 'tutor':
        if not user.perfil_tutor.ninos.filter(pk=nino.pk).exists():
            raise PermissionDenied

    contexto = {
        'control': control,
        'nino': nino
    }
    return render(request, 'control/ver_control.html', contexto)

@login_required
@rol_requerido(['Administrador', 'Profesional'])
def editar_control(request, control_id):
    control = get_object_or_404(Control, pk=control_id)
    nino = control.nino

    if request.method == 'POST':
        # La lógica es idéntica a la de 'registrar_control', simplemente actualizamos el objeto existente
        control.fecha_realizacion_control = request.POST.get('fecha_realizacion')
        control.pesokg = float(request.POST.get('pesokg'))
        control.talla_cm = float(request.POST.get('talla_cm'))
        control.pc_cm = request.POST.get('pc_cm') if request.POST.get('pc_cm') else None
        
        if control.talla_cm > 0:
            talla_m = control.talla_cm / 100
            control.imc = round(control.pesokg / (talla_m ** 2), 2)
        
        control.calificacion_nutricional = request.POST.get('calificacion_nutricional')
        control.calificacion_estatural = request.POST.get('calificacion_estatural')
        control.calificacion_pce = request.POST.get('calificacion_pce')
        control.dig_pa = request.POST.get('dig_pa')
        
        control.diag_des_integral = request.POST.get('diag_des_integral')
        control.obs_desarrollo_integral = request.POST.get('obs_desarrollo_integral')
        control.observaciones = request.POST.get('observaciones')
        control.indicaciones = request.POST.get('indicaciones')
        
        control.derivacion = 'derivacion' in request.POST
        control.consulta_dental_realizada = 'consulta_dental_realizada' in request.POST
        control.derivacion_dentista = 'derivacion_dentista' in request.POST

        control.save()
        messages.success(request, f'El "{control.nombre_control}" ha sido actualizado exitosamente.')
        return redirect('controles', nino_rut=nino.rut_nino)

    # Para la petición GET, pasamos los datos del control y las opciones a la plantilla
    contexto = {
        'control': control,
        'nino': nino,
        'estatural_choices': Control.CALIFICACION_ESTATURAL_CHOICES,
        'pce_choices': Control.CALIFICACION_PCE_CHOICES,
        'pa_choices': Control.DIG_PA_CHOICES,
    }
    return render(request, 'control/editar_control.html', contexto)

@login_required
@rol_requerido(['Administrador']) # <-- Solo accesible para Administradores
def historial_control(request, control_id):
    control = get_object_or_404(Control, pk=control_id)
    
    # Obtenemos todos los registros históricos para este control
    historial = control.history.all()
    
    # Procesamos el historial para que sea más fácil de mostrar en la plantilla
    # La librería nos permite comparar cada versión con la anterior
    for i in range(len(historial) - 1):
        version_actual = historial[i]
        version_anterior = historial[i+1]
        # 'diff_against' nos devuelve un objeto con los cambios
        delta = version_actual.diff_against(version_anterior)
        # Guardamos los cambios en el objeto para usarlos en la plantilla
        version_actual.cambios_calculados = delta.changes

    contexto = {
        'control': control,
        'historial': historial
    }
    return render(request, 'control/historial_control.html', contexto)


# control/views.py

@login_required
@rol_requerido(['Administrador'])
def configurar_periodos(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update':
            periodos = PeriodoControl.objects.all()
            hubo_cambios = False # Una bandera para saber si debemos recalcular

            for periodo in periodos:
                # Obtenemos los datos nuevos del formulario
                nuevo_nombre = request.POST.get(f'nombre_control_{periodo.id}')
                nuevo_mes = int(request.POST.get(f'mes_control_{periodo.id}'))
                nuevo_margen = int(request.POST.get(f'dias_margen_{periodo.id}'))

                # --- LÓGICA DE VERIFICACIÓN AÑADIDA ---
                # Comparamos los datos nuevos con los que ya tiene el objeto
                if (periodo.nombre_mes_control != nuevo_nombre or
                    periodo.mes_control != nuevo_mes or
                    periodo.dias_margen != nuevo_margen):
                    
                    # Si hay al menos una diferencia, actualizamos y guardamos
                    periodo.nombre_mes_control = nuevo_nombre
                    periodo.mes_control = nuevo_mes
                    periodo.dias_margen = nuevo_margen
                    periodo.save() # .save() solo se llama si hay cambios
                    hubo_cambios = True # Marcamos que hubo al menos un cambio
            
            # Si hubo al menos un cambio, recalculamos los calendarios
            if hubo_cambios:
                try:
                    call_command('recalcular_controles')
                    messages.success(request, 'La configuración ha sido guardada y los calendarios recalculados.')
                except Exception as e:
                    messages.error(request, f'Configuración guardada, pero error al recalcular: {e}')
            else:
                messages.info(request, 'No se detectaron cambios para guardar.')

        elif action == 'create':
            # ... (la lógica para crear un nuevo control no cambia)
            pass

        return redirect('configurar_periodos')

    # La lógica GET no cambia
    periodos = PeriodoControl.objects.all().order_by('mes_control')
    contexto = {'periodos': periodos}
    return render(request, 'control/configurar_periodos.html', contexto)

@login_required
@rol_requerido(['Administrador'])
def historial_configuracion(request):
    # Obtenemos el historial de todos los objetos PeriodoControl, ordenado por fecha
    historial = PeriodoControl.history.all().order_by('-history_date')
    
    # --- LÓGICA AÑADIDA PARA CALCULAR CAMBIOS ---
    for i in range(len(historial)):
        version_actual = historial[i]
        # Obtenemos el registro previo (si existe)
        version_anterior = version_actual.prev_record
        if version_anterior:
            delta = version_actual.diff_against(version_anterior)
            version_actual.cambios_calculados = delta.changes

    contexto = {
        'historial': historial
    }
    return render(request, 'control/historial_configuracion.html', contexto)