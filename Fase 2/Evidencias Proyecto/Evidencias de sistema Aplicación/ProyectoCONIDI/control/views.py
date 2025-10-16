from django.shortcuts import render, get_object_or_404, redirect   
from datetime import date, timedelta

from django.urls import reverse
from .models import Nino, Control, PeriodoControl, Vacuna, VacunaAplicada, Alergias, RegistroAlergias
from django.contrib.auth.decorators import login_required
from login.models import Tutor 
from django.core.exceptions import PermissionDenied 
from django.contrib import messages
from login.decorators import rol_requerido
from django.core.management import call_command
from simple_history.admin import SimpleHistoryAdmin
from django.db.models import Q
from django.db import IntegrityError

@login_required
def controles(request, nino_rut):
    # Obtenemos el niño que se está pidiendo en la URL
    nino = get_object_or_404(Nino, pk=nino_rut)
    user = request.user
    
    # --- Verificación de permisos (sin cambios) ---
    if user.rol.nombre_rol.lower() == 'tutor':
        if not user.perfil_tutor.ninos.filter(pk=nino.pk).exists():
            raise PermissionDenied
    
    # --- Obtención de datos ---
    # 1. Obtenemos los controles de niño sano (sin cambios)
    lista_controles = nino.controles.all().order_by('fecha_control_programada')

    # 2. OBTENEMOS LAS VACUNAS APLICADAS AL NIÑO 💉
    vacunas_aplicadas = nino.vacunas_aplicadas.all().order_by('-fecha_aplicacion')
    # 3. Obtenemos las alergias we 
    alergias_registradas = nino.alergias_registradas.all().order_by('-fecha_aparicion')
    # --- Preparamos el contexto para la plantilla ---
    contexto = {
        "nino": nino,
        "controles": lista_controles,
        "vacunas_aplicadas": vacunas_aplicadas,
        "alergias_registradas": alergias_registradas, # <-- AÑADIMOS LAS VACUNAS AL CONTEXTO
    }
    return render(request, 'control/controles.html', context=contexto)

@login_required
def listar_ninos(request):
    user = request.user
    rol_usuario = user.rol.nombre_rol.lower()

    # --- Capturamos los datos del formulario de filtros ---
    nombre_query = request.GET.get('nombre', '')
    rut_query = request.GET.get('rut', '')

    # Tu lógica original para obtener la lista base de niños
    lista_ninos = Nino.objects.none() # Por defecto, una lista vacía

    if rol_usuario in ['administrador', 'profesional']:
        # Si es admin o profesional, la lista base son todos los niños
        lista_ninos = Nino.objects.prefetch_related('ninotutor_set__tutor').all()
    
    elif rol_usuario == 'tutor':
        # Si es tutor, la lista base son solo sus niños asignados
        try:
            lista_ninos = user.perfil_tutor.ninos.prefetch_related('ninotutor_set__tutor').all()
        except Tutor.DoesNotExist:
            lista_ninos = Nino.objects.none()

    # --- Aplicamos los filtros sobre la lista base que obtuvimos ---
    if nombre_query:
        # Si se buscó un nombre, filtramos la lista usando Q para buscar en múltiples campos
        lista_ninos = lista_ninos.filter(
            Q(nombre__icontains=nombre_query) |
            Q(ap_paterno__icontains=nombre_query) |
            Q(ap_materno__icontains=nombre_query)
        )

    if rut_query:
        # Si se buscó un RUT, filtramos la lista (que ya podría estar filtrada por nombre)
        lista_ninos = lista_ninos.filter(rut_nino__icontains=rut_query)

    # Enviamos la lista final (ya filtrada y ordenada) al contexto
    contexto = {
        # Aseguramos el orden después de todos los filtros
        'ninos': lista_ninos.order_by('nombre', 'ap_paterno'),
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



@login_required
@rol_requerido(['Administrador', 'Profesional'])
def registrar_vacuna(request, nino_rut):
    nino = get_object_or_404(Nino, pk=nino_rut)

    if request.method == 'POST':
        vacuna_id = request.POST.get('vacuna')
        fecha_aplicacion = request.POST.get('fecha_aplicacion')
        dosis = request.POST.get('dosis')
        lugar = request.POST.get('lugar')

        # Obtenemos el objeto Vacuna completo usando su ID
        vacuna_obj = get_object_or_404(Vacuna, pk=vacuna_id)

        profesional_obj = None
        try:
            profesional_obj = request.user.perfil_profesional
        except:
            pass

        # --- LÍNEA CORREGIDA ---
        # Al crear el objeto, nos aseguramos de pasar el objeto 'vacuna_obj'
        # al campo 'vacuna' del modelo.
        VacunaAplicada.objects.create(
            nino=nino,
            vacuna=vacuna_obj, # <-- Cambio clave
            fecha_aplicacion=fecha_aplicacion,
            dosis=dosis,
            lugar=lugar,
            profesional=profesional_obj
        )
        messages.success(request, f"Vacuna '{vacuna_obj.nom_vacuna}' registrada para {nino.nombre}.")
        return redirect('controles', nino_rut=nino.rut_nino)

    # La lógica GET no cambia
    todas_las_vacunas = Vacuna.objects.all().order_by('nom_vacuna')
    contexto = {
        'nino': nino,
        'vacunas': todas_las_vacunas,
    }
    return render(request, 'control/registrar_vacuna.html', contexto)

@login_required
@rol_requerido(['Administrador', 'Profesional'])
def registrar_vacuna(request, vacuna_aplicada_id):
    vacuna_aplicada = get_object_or_404(VacunaAplicada, pk=vacuna_aplicada_id)
    nino = vacuna_aplicada.nino

    if request.method == 'POST':
        # Actualizamos el registro existente con los datos del formulario
        vacuna_aplicada.fecha_aplicacion = request.POST.get('fecha_aplicacion')
        vacuna_aplicada.dosis = request.POST.get('dosis')
        vacuna_aplicada.lugar = request.POST.get('lugar')
        vacuna_aplicada.via = request.POST.get('via')

        try:
            vacuna_aplicada.profesional = request.user.perfil_profesional
        except:
            pass # Si es un admin, no tiene perfil de profesional

        vacuna_aplicada.save()
        messages.success(request, f"Vacuna '{vacuna_aplicada.vacuna.nom_vacuna}' registrada exitosamente.")
        return redirect('controles', nino_rut=nino.rut_nino)

    contexto = {
        'vacuna_aplicada': vacuna_aplicada,
        'nino': nino,
        'via_choices': VacunaAplicada.VIA_CHOICES, # Pasamos las opciones para el menú
    }
    return render(request, 'control/registrar_vacuna.html', contexto)

@login_required
def ver_vacuna(request, vacuna_aplicada_id):
    vacuna_aplicada = get_object_or_404(VacunaAplicada, pk=vacuna_aplicada_id)
    nino = vacuna_aplicada.nino

    # Verificación de seguridad para tutores
    if request.user.rol.nombre_rol.lower() == 'tutor':
        if not request.user.perfil_tutor.ninos.filter(pk=nino.pk).exists():
            raise PermissionDenied

    contexto = {
        'vacuna_aplicada': vacuna_aplicada,
        'nino': nino
    }
    return render(request, 'control/ver_vacuna.html', contexto)

@login_required
@rol_requerido(['Administrador', 'Profesional'])
def editar_vacuna(request, vacuna_aplicada_id):
    vacuna_aplicada = get_object_or_404(VacunaAplicada, pk=vacuna_aplicada_id)
    nino = vacuna_aplicada.nino

    if request.method == 'POST':
        # La lógica de guardar los datos del formulario no cambia
        vacuna_aplicada.fecha_aplicacion = request.POST.get('fecha_aplicacion')
        vacuna_aplicada.dosis = request.POST.get('dosis')
        vacuna_aplicada.lugar = request.POST.get('lugar')
        vacuna_aplicada.via = request.POST.get('via')
        
        # --- LÓGICA AÑADIDA PARA REGISTRAR QUIÉN EDITA ---
        # Se actualiza el profesional al que realizó la última modificación.
        try:
            vacuna_aplicada.profesional = request.user.perfil_profesional
        except:
            # Si el usuario es un Admin sin perfil de profesional, el campo no se modifica.
            pass
        # -------------------------------------------------

        vacuna_aplicada.save()
        
        messages.success(request, f"Registro de vacuna '{vacuna_aplicada.vacuna.nom_vacuna}' actualizado.")
        return redirect('controles', nino_rut=nino.rut_nino)

    # La lógica para la petición GET no cambia
    contexto = {
        'vacuna_aplicada': vacuna_aplicada,
        'nino': nino,
        'via_choices': VacunaAplicada.VIA_CHOICES,
    }
    return render(request, 'control/editar_vacuna.html', contexto)

@login_required
@rol_requerido(['Administrador']) # Solo para Administradores
def historial_vacuna(request, vacuna_aplicada_id):
    vacuna_aplicada = get_object_or_404(VacunaAplicada, pk=vacuna_aplicada_id)

    # Obtenemos el historial usando la misma lógica que en los controles
    historial = vacuna_aplicada.history.all()
    for i in range(len(historial) - 1):
        version_actual = historial[i]
        version_anterior = historial[i+1]
        delta = version_actual.diff_against(version_anterior)
        version_actual.cambios_calculados = delta.changes

    contexto = {
        'vacuna_aplicada': vacuna_aplicada,
        'historial': historial
    }
    return render(request, 'control/historial_vacuna.html', contexto)

@login_required
@rol_requerido(['Administrador'])
def configurar_vacunas(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update':
            vacunas = Vacuna.objects.all()
            for vacuna in vacunas:
                nuevo_nombre = request.POST.get(f'nombre_vacuna_{vacuna.id}')
                nuevo_mes = request.POST.get(f'meses_programada_{vacuna.id}')

                # Convertimos el mes a entero o None si está vacío
                if nuevo_mes:
                    nuevo_mes = int(nuevo_mes)
                else:
                    nuevo_mes = None
                
                # Guardamos solo si hay cambios
                if (vacuna.nom_vacuna != nuevo_nombre or vacuna.meses_programada != nuevo_mes):
                    vacuna.nom_vacuna = nuevo_nombre
                    vacuna.meses_programada = nuevo_mes
                    vacuna.save()
            
            messages.success(request, 'La configuración de vacunas ha sido actualizada.')
            # Aquí podríamos llamar a un futuro 'recalcular_vacunas'

        elif action == 'create':
            nuevo_nombre = request.POST.get('nuevo_nombre')
            nuevo_mes = request.POST.get('nuevo_mes')

            if nuevo_nombre and nuevo_mes:
                Vacuna.objects.create(
                    nom_vacuna=nuevo_nombre,
                    meses_programada=int(nuevo_mes)
                )
                messages.success(request, f'Nueva vacuna "{nuevo_nombre}" agregada.')

        return redirect('configurar_vacunas')

    # Para la petición GET
    vacunas = Vacuna.objects.all().order_by('meses_programada', 'nom_vacuna')
    contexto = {'vacunas': vacunas}
    return render(request, 'control/configurar_vacunas.html', contexto)

@login_required
@rol_requerido(['Administrador'])
def historial_vacunas(request):
    # Obtenemos el historial de todos los objetos Vacuna
    historial = Vacuna.history.all().order_by('-history_date')

    # Calculamos los cambios entre versiones
    for i in range(len(historial)):
        version_actual = historial[i]
        version_anterior = version_actual.prev_record
        if version_anterior:
            delta = version_actual.diff_against(version_anterior)
            version_actual.cambios_calculados = delta.changes

    contexto = {
        'historial': historial
    }
    return render(request, 'control/historial_configuracion_vacunas.html', contexto)

# control/views.py

# 1. Asegúrate de que 'reverse' esté importado al principio del archivo
from django.urls import reverse
# ... (tus otros imports)


@login_required
@rol_requerido(['Administrador', 'Profesional'])
def registrar_alergia(request, nino_rut):
    nino = get_object_or_404(Nino, pk=nino_rut)
    
    if request.method == 'POST':
        alergia_id = request.POST.get('alergia')
        fecha_aparicion = request.POST.get('fecha_aparicion')
        observaciones = request.POST.get('observaciones')
        
        alergia_obj = get_object_or_404(Alergias, pk=alergia_id)
        
        RegistroAlergias.objects.create(
            nino=nino,
            alergia=alergia_obj,
            fecha_aparicion=fecha_aparicion,
            observaciones=observaciones
        )
        
        messages.success(request, f"Alergia a '{alergia_obj.tipo_alergia}' registrada para {nino.nombre}.")

        # --- LÓGICA DE REDIRECCIÓN ACTUALIZADA ---
        # Construimos la URL base usando reverse()
        url_base = reverse('controles', kwargs={'nino_rut': nino.rut_nino})
        # Le añadimos el ancla para la pestaña de alergias
        url_con_pestaña = f"{url_base}#alergias-pane"
        # Redirigimos a la URL completa
        return redirect(url_con_pestaña)

    # La lógica GET no cambia
    contexto = {
        'nino': nino,
        'alergias_disponibles': Alergias.objects.all()
    }
    return render(request, 'control/registrar_alergia.html', contexto)

@login_required
@rol_requerido(['Administrador', 'Profesional'])
def editar_alergia(request, registro_alergia_id):
    # Obtenemos el registro específico de la alergia que se quiere editar
    registro = get_object_or_404(RegistroAlergias, pk=registro_alergia_id)
    nino = registro.nino

    if request.method == 'POST':
        # Actualizamos los campos con los datos del formulario
        registro.fecha_aparicion = request.POST.get('fecha_aparicion')
        registro.observaciones = request.POST.get('observaciones')
        
        # El campo de fecha de remisión es opcional
        fecha_remision = request.POST.get('fecha_remision')
        if fecha_remision:
            registro.fecha_remision = fecha_remision
        else:
            registro.fecha_remision = None # Guardamos null si el campo está vacío

        registro.save()
        
        messages.success(request, f"El registro de alergia a '{registro.alergia.tipo_alergia}' ha sido actualizado.")
        return redirect('controles', nino_rut=nino.rut_nino)

    # Para la petición GET, mostramos el formulario con los datos existentes
    contexto = {
        'registro': registro,
        'nino': nino
    }
    return render(request, 'control/editar_alergia.html', contexto)

@login_required
@rol_requerido(['Administrador']) # Solo para Administradores
def historial_alergia(request, registro_alergia_id):
    registro = get_object_or_404(RegistroAlergias, pk=registro_alergia_id)

    # Obtenemos el historial usando la misma lógica que en los otros modelos
    historial = registro.history.all()
    for i in range(len(historial) - 1):
        version_actual = historial[i]
        version_anterior = historial[i+1]
        delta = version_actual.diff_against(version_anterior)
        version_actual.cambios_calculados = delta.changes

    contexto = {
        'registro': registro,
        'historial': historial
    }
    return render(request, 'control/historial_alergia.html', contexto)

@login_required
@rol_requerido(['Administrador'])
def configurar_alergias(request):
    if request.method == 'POST':
        # Obtenemos el 'action' que nos envía el botón presionado
        action = request.POST.get('action', '')

        # --- Lógica para ACTUALIZAR ---
        if action == 'update':
            for alergia in Alergias.objects.all():
                nuevo_nombre = request.POST.get(f'tipo_alergia_{alergia.id}')
                if nuevo_nombre and alergia.tipo_alergia != nuevo_nombre:
                    alergia.tipo_alergia = nuevo_nombre
                    alergia.save()
            messages.success(request, 'La lista de alergias ha sido actualizada.')

        # --- Lógica para ELIMINAR ---
        elif action.startswith('delete_'):
            # Si el 'action' empieza con 'delete_', sabemos que se presionó un botón de eliminar
            alergia_id = action.split('_')[1] # Extraemos el ID del valor 'delete_123'
            try:
                alergia = Alergias.objects.get(pk=alergia_id)
                nombre_alergia = alergia.tipo_alergia
                alergia.delete()
                messages.success(request, f'La alergia "{nombre_alergia}" ha sido eliminada.')
            except IntegrityError:
                messages.error(request, 'No se puede eliminar esta alergia porque ya está asignada a uno o más niños.')
            except Alergias.DoesNotExist:
                messages.error(request, 'La alergia que intentas eliminar no existe.')

        # --- Lógica para CREAR ---
        elif action == 'create':
            nuevo_nombre = request.POST.get('nuevo_nombre')
            if nuevo_nombre:
                Alergias.objects.create(tipo_alergia=nuevo_nombre)
                messages.success(request, f'El tipo de alergia "{nuevo_nombre}" ha sido agregado.')
        
        return redirect('configurar_alergias')

    # La lógica GET no cambia
    alergias = Alergias.objects.all().order_by('tipo_alergia')
    contexto = {'alergias': alergias}
    return render(request, 'control/configurar_alergias.html', contexto)
@login_required
@rol_requerido(['Administrador'])
def historial_alergias(request):
    # La lógica para obtener el historial no cambia
    historial = Alergias.history.all().order_by('-history_date')
    
    for i in range(len(historial)):
        version_actual = historial[i]
        version_anterior = version_actual.prev_record
        if version_anterior:
            delta = version_actual.diff_against(version_anterior)
            version_actual.cambios_calculados = delta.changes

    contexto = {
        'historial': historial
    }

    return render(request, 'control/historial_alergias_tipo.html', contexto)