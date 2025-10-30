from django.shortcuts import render, get_object_or_404, redirect   
from datetime import date, timedelta
from django.db import transaction
from django.urls import reverse
from unidecode import unidecode
from .models import Nino, Control, PeriodoControl, Vacuna, VacunaAplicada, RegistroAlergias, CategoriaAlergia
from django.contrib.auth.decorators import login_required
from login.models import Tutor, Profesional
from django.core.exceptions import PermissionDenied 
from django.contrib import messages
from login.decorators import rol_requerido
from django.core.management import call_command
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from simple_history.admin import SimpleHistoryAdmin
from django.db.models import Q
from django.db import IntegrityError
from django.urls import reverse



@login_required
def controles(request, nino_rut): # Vista renombrada mentalmente a 'detalle_nino'
    nino = get_object_or_404(Nino.objects.select_related('comuna'), pk=nino_rut) # Optimizamos comuna
    user = request.user

    # Verificación de permisos para tutores
    if user.rol.nombre_rol.lower() == 'tutor':
        try:
            if not user.perfil_tutor.ninos.filter(pk=nino.pk).exists():
                raise PermissionDenied
        except Tutor.DoesNotExist:
             raise PermissionDenied # Si es rol tutor pero no tiene perfil, denegar

    # Obtención de datos para las pestañas
    lista_controles = nino.controles.select_related('periodo').all().order_by('fecha_control_programada')
    vacunas_aplicadas = nino.vacunas_aplicadas.select_related('vacuna').all().order_by('fecha_programada')
    alergias_registradas = nino.alergias_registradas.select_related('categoria').all().order_by('-fecha_aparicion')

    # --- LÓGICA NECESARIA PARA LA PESTAÑA RESUMEN ---
    ultimo_control = nino.controles.filter(
        fecha_realizacion_control__isnull=False, 
        deshabilitado=False                     
    ).order_by('-fecha_realizacion_control').first() 
    # ---------------------------------------------------

    contexto = {
        "nino": nino,
        "controles": lista_controles,
        "vacunas_aplicadas": vacunas_aplicadas,
        "alergias_registradas": alergias_registradas,
        "ultimo_control": ultimo_control, # <-- Variable añadida para la pestaña Resumen
    }
    # Asegúrate que la ruta de la plantilla sea correcta
    return render(request, 'control/nino/controles.html', contexto)

@login_required
def listar_ninos(request):
    user = request.user
    rol_usuario = user.rol.nombre_rol.lower()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'enviar_correo_pnac':
            nino_rut = request.POST.get('nino_rut')
            nino = get_object_or_404(Nino, rut_nino=nino_rut)
            
            # Buscamos la primera relación tutor-niño para obtener el tutor
            relacion = nino.ninotutor_set.select_related('tutor').first()

            if relacion and relacion.tutor and relacion.tutor.email:
                tutor = relacion.tutor
                asunto = "Notificación: Arribo de Alimentos PNAC"
                mensaje = (
                    f"Estimado/a {tutor.nombre_completo},\n\n"
                    f"Le informamos que han llegado los alimentos del Programa de Alimentación Complementaria (PNAC) para {nino.nombre} {nino.ap_paterno} {nino.ap_materno}.\n\n"
                    "Puede acercarse a nuestro CESFAM para realizar el retiro.\n\n"
                    "Horario de atención: [Completar con el horario de retiro]\n\n"
                    "Atentamente,\n"
                    "Equipo CESFAM"
                )
                try:
                    send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [tutor.email])
                    messages.success(request, f"Correo de notificación PNAC enviado exitosamente a {tutor.email}.")
                except Exception as e:
                    messages.error(request, f"Error al enviar el correo a {tutor.email}: {e}")
            else:
                messages.warning(request, f"No se pudo enviar el correo: el niño/a {nino.nombre_completo} no tiene un tutor con email asignado.")
            return redirect('control:listar_ninos')

    # --- Capturamos los datos del formulario de filtros ---
    nombre_query = request.GET.get('nombre', '')
    rut_query = request.GET.get('rut', '')

    # Obtener la lista base de niños
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

    # Se aplican los filtros sobre la lista base que obtuvimos 
    if nombre_query:
        # Si se buscó un nombre, filtramos la lista usando Q para buscar en múltiples campos
        nombre_query_norm = unidecode(nombre_query).lower()
        lista_ninos = lista_ninos.filter(
            Q(nombre_norm__icontains=nombre_query_norm) |
            Q(ap_paterno_norm__icontains=nombre_query_norm) |
            Q(ap_materno_norm__icontains=nombre_query_norm)
        )

    if rut_query:
        # Si se buscó un RUT, filtramos la lista (que ya podría estar filtrada por nombre)
        lista_ninos = lista_ninos.filter(rut_nino__icontains=rut_query)

    # Enviamos la lista final (ya filtrada y ordenada) al contexto
    contexto = {
        # Aseguramos el orden después de todos los filtros
        'ninos': lista_ninos.order_by('nombre', 'ap_paterno'),
        'rol_usuario': rol_usuario, # <--- Pasa el rol a la plantilla
    }
    return render(request, 'control/nino/listar_ninos.html', contexto)

@login_required
@rol_requerido(['Administrador', 'Profesional'])
def registrar_control(request, control_id):
    control = get_object_or_404(Control, pk=control_id)
    nino = control.nino

    contexto = {
        'control': control,
        'nino': nino,
        'estatural_choices': Control.CALIFICACION_ESTATURAL_CHOICES,
        'pce_choices': Control.CALIFICACION_PCE_CHOICES,
        'pa_choices': Control.DIG_PA_CHOICES,
    }

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'disable':
            # ... (esta lógica ya está bien, limpia todos los campos) ...
            control.deshabilitado = True
            control.estado_control = 'Deshabilitado'
            control.fecha_realizacion_control = None
            control.pesokg = None
            control.talla_cm = None
            control.imc = None
            control.pc_cm = None
            control.calificacion_nutricional = None
            control.calificacion_estatural = None
            control.calificacion_pce = None
            control.dig_pa = None
            control.diag_des_integral = None
            control.obs_desarrollo_integral = None
            control.observaciones = None
            control.indicaciones = None
            control.derivacion = False
            control.consulta_dental_realizada = None
            control.derivacion_dentista = None
            control.profesional = None
            control.save()
            messages.warning(request, f'El "{control.nombre_control}" ha sido marcado como No Realizado/No Aplica.')
            return redirect('control:detalle_nino', nino_rut=nino.rut_nino)

        # --- VALIDACIÓN DE GUARDADO NORMAL ---
        
        errores_validacion = []
        try:
            # 1. Validar y convertir campos numéricos
            pesokg_str = request.POST.get('pesokg')
            talla_cm_str = request.POST.get('talla_cm')
            control.pesokg = float(pesokg_str) if pesokg_str else None
            control.talla_cm = float(talla_cm_str) if talla_cm_str else None
            
            pc_cm_str = request.POST.get('pc_cm')
            control.pc_cm = float(pc_cm_str) if pc_cm_str else None

            # 2. Validar rangos lógicos
            if control.pesokg and (control.pesokg <= 0 or control.pesokg > 150):
                errores_validacion.append(f"El peso ({control.pesokg} kg) está fuera del rango lógico (0-150 kg).")
            if control.talla_cm and (control.talla_cm <= 20 or control.talla_cm > 250):
                errores_validacion.append(f"La talla ({control.talla_cm} cm) está fuera del rango lógico (20-250 cm).")
            if control.pc_cm and (control.pc_cm <= 10 or control.pc_cm > 100):
                errores_validacion.append(f"El P. Craneal ({control.pc_cm} cm) está fuera del rango lógico (10-100 cm).")

            # 3. Validar fecha
            fecha_realizacion_str = request.POST.get('fecha_realizacion')
            if not fecha_realizacion_str:
                errores_validacion.append("La fecha de realización es obligatoria.")
            else:
                control.fecha_realizacion_control = date.fromisoformat(fecha_realizacion_str)
                if control.fecha_realizacion_control > date.today():
                    errores_validacion.append("La fecha de realización no puede ser en el futuro.")
                if control.fecha_realizacion_control < nino.fecha_nacimiento:
                     errores_validacion.append("La fecha de realización no puede ser anterior a la fecha de nacimiento del niño.")

        except (ValueError, TypeError):
            errores_validacion.append('Peso, Talla o P. Craneal deben ser números válidos.')
        
        # Si se encontró algún error, regresar al formulario
        if errores_validacion:
            for error in errores_validacion:
                messages.error(request, error)
            contexto['form_data'] = request.POST
            return render(request, 'control/control_nino_sano/registrar_control.html', contexto)

        # --- Si todo está bien, continuar con el guardado ---
        
        if control.talla_cm and control.talla_cm > 0 and control.pesokg:
            talla_m = control.talla_cm / 100
            control.imc = round(control.pesokg / (talla_m ** 2), 2)
        else:
             control.imc = None

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
        control.estado_control = 'Realizado'
        control.deshabilitado = False 

        try:
            control.profesional = request.user.perfil_profesional
        except Profesional.DoesNotExist:
            pass

        control.save()
        messages.success(request, f'El "{control.nombre_control}" ha sido registrado exitosamente.')
        return redirect('control:detalle_nino', nino_rut=nino.rut_nino)

    return render(request, 'control/control_nino_sano/registrar_control.html', contexto)


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
    return render(request, 'control/control_nino_sano/ver_control.html', contexto)

@login_required
@rol_requerido(['Administrador', 'Profesional'])
def editar_control(request, control_id):
    control = get_object_or_404(Control, pk=control_id)
    nino = control.nino

    # Preparamos el contexto base para la vista GET y para errores en POST
    contexto = {
        'control': control,
        'nino': nino,
        'estatural_choices': Control.CALIFICACION_ESTATURAL_CHOICES,
        'pce_choices': Control.CALIFICACION_PCE_CHOICES,
        'pa_choices': Control.DIG_PA_CHOICES,
    }

    if request.method == 'POST':
        action = request.POST.get('action')

        # --- LÓGICA PARA DESHABILITAR EL CONTROL ---
        if action == 'disable':
            control.deshabilitado = True
            control.estado_control = 'Deshabilitado'
            # Limpia todos los campos clínicos para evitar datos inconsistentes
            control.fecha_realizacion_control = None
            control.pesokg = None
            control.talla_cm = None
            control.imc = None
            control.pc_cm = None
            control.calificacion_nutricional = None
            control.calificacion_estatural = None
            control.calificacion_pce = None
            control.dig_pa = None
            control.diag_des_integral = None
            control.obs_desarrollo_integral = None
            control.observaciones = None
            control.indicaciones = None
            control.derivacion = False
            control.consulta_dental_realizada = None
            control.derivacion_dentista = None
            # Opcional: limpiar el profesional, depende de si quieres guardar quién lo deshabilitó
            # control.profesional = None

            control.save()
            messages.warning(request, f'El "{control.nombre_control}" ha sido marcado como No Realizado/No Aplica.')
            return redirect('control:detalle_nino', nino_rut=nino.rut_nino)

        # --- LÓGICA PARA GUARDAR CAMBIOS (ACCIÓN 'save' O POR DEFECTO) ---

        errores_validacion = []
        try:
            # 1. Validar y convertir campos numéricos
            pesokg_str = request.POST.get('pesokg')
            talla_cm_str = request.POST.get('talla_cm')
            pc_cm_str = request.POST.get('pc_cm')

            peso_kg = float(pesokg_str) if pesokg_str else None
            talla_cm = float(talla_cm_str) if talla_cm_str else None
            pc_cm = float(pc_cm_str) if pc_cm_str else None

            # 2. Validar rangos lógicos
            if peso_kg is not None and (peso_kg <= 0 or peso_kg > 150):
                errores_validacion.append(f"El peso ({peso_kg} kg) está fuera del rango lógico (0-150 kg).")
            if talla_cm is not None and (talla_cm <= 20 or talla_cm > 250):
                errores_validacion.append(f"La talla ({talla_cm} cm) está fuera del rango lógico (20-250 cm).")
            if pc_cm is not None and (pc_cm <= 10 or pc_cm > 100):
                errores_validacion.append(f"El P. Craneal ({pc_cm} cm) está fuera del rango lógico (10-100 cm).")

            # 3. Validar fecha
            fecha_realizacion_str = request.POST.get('fecha_realizacion')
            if not fecha_realizacion_str:
                errores_validacion.append("La fecha de realización es obligatoria.")
            else:
                fecha_realizacion = date.fromisoformat(fecha_realizacion_str)
                if fecha_realizacion > date.today():
                    errores_validacion.append("La fecha de realización no puede ser en el futuro.")
                if fecha_realizacion < nino.fecha_nacimiento:
                     errores_validacion.append("La fecha de realización no puede ser anterior a la fecha de nacimiento del niño.")

        except (ValueError, TypeError):
            errores_validacion.append('Peso, Talla o P. Craneal deben ser números válidos.')

        # Si se encontró algún error, regresar al formulario mostrando los mensajes
        if errores_validacion:
            for error in errores_validacion:
                messages.error(request, error)
            contexto['form_data'] = request.POST # Pasa los datos del POST para rellenar el form
            return render(request, 'control/control_nino_sano/editar_control.html', contexto)

        # --- Si todo está bien, continuar con el guardado de datos ---

        # Asignamos los valores ya validados y convertidos
        control.fecha_realizacion_control = fecha_realizacion
        control.pesokg = peso_kg
        control.talla_cm = talla_cm
        control.pc_cm = pc_cm

        # Recalcular IMC
        if control.talla_cm and control.talla_cm > 0 and control.pesokg:
            talla_m = control.talla_cm / 100
            control.imc = round(control.pesokg / (talla_m ** 2), 2)
        else:
            control.imc = None

        # Asignar resto de campos desde el POST
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

        # Actualizar estado y asegurar que no esté deshabilitado
        control.estado_control = 'Realizado'
        control.deshabilitado = False

        # Opcional: Actualizar el profesional que hizo la última edición
        try:
            control.profesional = request.user.perfil_profesional
        except Profesional.DoesNotExist:
            pass # Mantiene el profesional original si es un admin

        control.save()
        messages.success(request, f'El "{control.nombre_control}" ha sido actualizado exitosamente.')
        return redirect('control:detalle_nino', nino_rut=nino.rut_nino)

    # Lógica para la petición GET (cuando se carga la página por primera vez)
    return render(request, 'control/control_nino_sano/editar_control.html', contexto)

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
    return render(request, 'control/control_nino_sano/historial_control.html', contexto)


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

        return redirect('control:configurar_periodos')

    # La lógica GET no cambia
    periodos = PeriodoControl.objects.all().order_by('mes_control')
    contexto = {'periodos': periodos}
    return render(request, 'control/config/configurar_periodos.html', contexto)

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
    return render(request, 'control/config/historial_configuracion.html', contexto)



@login_required
@rol_requerido(['Administrador', 'Profesional'])
def registrar_vacuna(request, vacuna_aplicada_id):
    vacuna_aplicada = get_object_or_404(VacunaAplicada, pk=vacuna_aplicada_id)
    nino = vacuna_aplicada.nino

    contexto = {
        'vacuna_aplicada': vacuna_aplicada,
        'nino': nino,
        'via_choices': VacunaAplicada.VIA_CHOICES,
    }

    if request.method == 'POST':
        action = request.POST.get('action') # Obtenemos la acción

        if action == 'disable':
            vacuna_aplicada.deshabilitado = True
            vacuna_aplicada.fecha_aplicacion = None # Limpiamos
            vacuna_aplicada.dosis = None
            vacuna_aplicada.lugar = None
            vacuna_aplicada.profesional = None
            vacuna_aplicada.save()
            messages.warning(request, f"La vacuna '{vacuna_aplicada.vacuna.nom_vacuna}' ha sido marcada como No Aplica.")
            return redirect('control:detalle_nino', nino_rut=nino.rut_nino)

        # Si no es 'disable', es guardado normal
        vacuna_aplicada.fecha_aplicacion = request.POST.get('fecha_aplicacion')
        vacuna_aplicada.dosis = request.POST.get('dosis')
        vacuna_aplicada.lugar = request.POST.get('lugar')
        vacuna_aplicada.via = request.POST.get('via')
        vacuna_aplicada.deshabilitado = False # Nos aseguramos que esté activa

        try:
            vacuna_aplicada.profesional = request.user.perfil_profesional
        except Profesional.DoesNotExist:
            pass 

        vacuna_aplicada.save()
        messages.success(request, f"Vacuna '{vacuna_aplicada.vacuna.nom_vacuna}' registrada exitosamente.")
        return redirect('control:detalle_nino', nino_rut=nino.rut_nino)

    return render(request, 'control/vacuna/registrar_vacuna.html', contexto)

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
    return render(request, 'control/vacuna/ver_vacuna.html', contexto)

@login_required
@rol_requerido(['Administrador', 'Profesional'])
def editar_vacuna(request, vacuna_aplicada_id):
    vacuna_aplicada = get_object_or_404(VacunaAplicada, pk=vacuna_aplicada_id)
    nino = vacuna_aplicada.nino

    contexto = {
        'vacuna_aplicada': vacuna_aplicada,
        'nino': nino,
        'via_choices': VacunaAplicada.VIA_CHOICES,
    }

    if request.method == 'POST':
        action = request.POST.get('action') # Obtenemos la acción

        if action == 'disable':
            vacuna_aplicada.deshabilitado = True
            vacuna_aplicada.fecha_aplicacion = None
            vacuna_aplicada.dosis = None
            vacuna_aplicada.lugar = None
            # No limpiamos el profesional, para saber quién la deshabilitó
            vacuna_aplicada.save()
            messages.warning(request, f"La vacuna '{vacuna_aplicada.vacuna.nom_vacuna}' ha sido marcada como No Aplica.")
            return redirect('control:detalle_nino', nino_rut=nino.rut_nino)

        # Si no es 'disable', es guardado normal
        vacuna_aplicada.fecha_aplicacion = request.POST.get('fecha_aplicacion')
        vacuna_aplicada.dosis = request.POST.get('dosis')
        vacuna_aplicada.lugar = request.POST.get('lugar')
        vacuna_aplicada.via = request.POST.get('via')
        vacuna_aplicada.deshabilitado = False # La reactivamos si se edita

        try:
            vacuna_aplicada.profesional = request.user.perfil_profesional
        except Profesional.DoesNotExist:
            pass

        vacuna_aplicada.save()
        messages.success(request, f"Registro de vacuna '{vacuna_aplicada.vacuna.nom_vacuna}' actualizado.")
        return redirect('control:detalle_nino', nino_rut=nino.rut_nino)

    return render(request, 'control/vacuna/editar_vacuna.html', contexto)

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
    return render(request, 'control/vacuna/historial_vacuna.html', contexto)

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

        return redirect('control:configurar_vacunas')

    # Para la petición GET
    vacunas = Vacuna.objects.all().order_by('meses_programada', 'nom_vacuna')
    contexto = {'vacunas': vacunas}
    return render(request, 'control/vacuna/configurar_vacunas.html', contexto)

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
    return render(request, 'control/config/historial_configuracion_vacunas.html', contexto)

# control/views.py



@login_required
@rol_requerido(['Administrador', 'Profesional'])
def registrar_alergia(request, nino_rut):
    nino = get_object_or_404(Nino, pk=nino_rut)
    
    if request.method == 'POST':
        categoria_id = request.POST.get('categoria')
        agente = request.POST.get('agente_especifico')
        mecanismo = request.POST.get('mecanismo_inmunitario')
        fecha_aparicion = request.POST.get('fecha_aparicion')
        observaciones = request.POST.get('observaciones')
        
        categoria_obj = get_object_or_404(CategoriaAlergia, pk=categoria_id)

        # Verificamos si ya existe
        if RegistroAlergias.objects.filter(nino=nino, categoria=categoria_obj, agente_especifico=agente).exists():
            messages.error(request, f"El niño/a ya tiene un registro para '{agente}' en la categoría '{categoria_obj.nombre}'.")
        else:
            RegistroAlergias.objects.create(
                nino=nino,
                categoria=categoria_obj,
                agente_especifico=agente,
                mecanismo_inmunitario=mecanismo,
                fecha_aparicion=fecha_aparicion,
                observaciones=observaciones
            )
            messages.success(request, f"Alergia a '{agente}' registrada para {nino.nombre}.")
        
        url_base = reverse('control:detalle_nino', kwargs={'nino_rut': nino.rut_nino})
        return redirect(f"{url_base}#alergias-pane")

    contexto = {
        'nino': nino,
        'categorias_disponibles': CategoriaAlergia.objects.all(),
        'mecanismos_choices': RegistroAlergias.TIPO_HIPERSENSIBILIDAD_CHOICES, # Choices desde RegistroAlergias
    }
    return render(request, 'control/alergia/registrar_alergia.html', contexto)

@rol_requerido(['Administrador', 'Profesional'])
def editar_alergia(request, registro_alergia_id):
    registro = get_object_or_404(RegistroAlergias, pk=registro_alergia_id)
    nino = registro.nino

    if request.method == 'POST':
        categoria_id = request.POST.get('categoria')
        agente = request.POST.get('agente_especifico')
        mecanismo = request.POST.get('mecanismo_inmunitario')
        fecha_aparicion = request.POST.get('fecha_aparicion')
        fecha_remision = request.POST.get('fecha_remision')
        observaciones = request.POST.get('observaciones')

        categoria_obj = get_object_or_404(CategoriaAlergia, pk=categoria_id)

        # Verificamos si la combinación ya existe PARA OTRO registro del mismo niño
        existe_duplicado = RegistroAlergias.objects.filter(
            nino=nino,
            categoria=categoria_obj,
            agente_especifico=agente
        ).exclude(pk=registro.pk).exists() # Excluimos el registro actual de la verificación

        if existe_duplicado:
            messages.error(request, f"Ya existe un registro para '{agente}' en la categoría '{categoria_obj.nombre}' para este niño/a.")
        else:
            # Actualizamos los campos
            registro.categoria = categoria_obj
            registro.agente_especifico = agente
            registro.mecanismo_inmunitario = mecanismo
            registro.fecha_aparicion = fecha_aparicion
            registro.observaciones = observaciones
            registro.fecha_remision = fecha_remision if fecha_remision else None
            
            registro.save()
            messages.success(request, f"El registro de alergia a '{registro.agente_especifico}' ha sido actualizado.")
        
        url_base = reverse('control:detalle_nino', kwargs={'nino_rut': nino.rut_nino})
        return redirect(f"{url_base}#alergias-pane")

    # Para la petición GET
    contexto = {
        'registro': registro,
        'nino': nino,
        'categorias_disponibles': CategoriaAlergia.objects.all(),
        'mecanismos_choices': RegistroAlergias.TIPO_HIPERSENSIBILIDAD_CHOICES,
    }
    return render(request, 'control/alergia/editar_alergia.html', contexto)

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
    return render(request, 'control/alergia/historial_alergia.html', contexto)

@login_required
@rol_requerido(['Administrador'])
def configurar_categorias_alergia(request): # <- Nombre actualizado
    if request.method == 'POST':
        action = request.POST.get('action')

        # Bandera para saber si se realizó alguna acción exitosa
        accion_exitosa = False

        if action == 'update':
            for categoria in CategoriaAlergia.objects.all():
                nuevo_nombre = request.POST.get(f'nombre_categoria_{categoria.id}')
                if nuevo_nombre and categoria.nombre != nuevo_nombre:
                    # Verificamos si el nuevo nombre ya existe
                    if CategoriaAlergia.objects.filter(nombre=nuevo_nombre).exclude(pk=categoria.id).exists():
                        messages.error(request, f'Ya existe una categoría llamada "{nuevo_nombre}".')
                    else:
                        categoria.nombre = nuevo_nombre
                        categoria.save()
                        accion_exitosa = True
            if accion_exitosa:
                messages.success(request, 'La lista de categorías ha sido actualizada.')

        elif action == 'create':
            nuevo_nombre = request.POST.get('nuevo_nombre')
            if nuevo_nombre:
                # Verificamos si ya existe antes de crear
                if not CategoriaAlergia.objects.filter(nombre=nuevo_nombre).exists():
                    CategoriaAlergia.objects.create(nombre=nuevo_nombre)
                    messages.success(request, f'Nueva categoría "{nuevo_nombre}" agregada.')
                else:
                    messages.warning(request, f'La categoría "{nuevo_nombre}" ya existe.')

        elif action == 'delete':
            categoria_id = request.POST.get('categoria_id')
            try:
                categoria = CategoriaAlergia.objects.get(pk=categoria_id)
                nombre_categoria = categoria.nombre
                # IMPORTANTE: Verificamos si está en uso en RegistroAlergias
                if RegistroAlergias.objects.filter(categoria=categoria).exists():
                    messages.error(request, f'No se puede eliminar "{nombre_categoria}" porque está asignada a uno o más niños.')
                else:
                    categoria.delete()
                    messages.success(request, f'La categoría "{nombre_categoria}" ha sido eliminada.')
            except CategoriaAlergia.DoesNotExist:
                messages.error(request, 'La categoría que intentas eliminar no existe.')
        
        return redirect('configurar_categorias_alergia') # <- Nombre actualizado

    # Para la petición GET
    categorias = CategoriaAlergia.objects.all().order_by('nombre')
    contexto = {'categorias': categorias}
    return render(request, 'control/config/configurar_categorias_alergia.html', contexto) # <- Nombre actualizado


@login_required
@rol_requerido(['Administrador'])
def historial_categorias_alergia(request): # <-- Asegúrate que la función tenga este nombre
    historial = CategoriaAlergia.history.all().order_by('-history_date')
    
    for i in range(len(historial)):
        version_actual = historial[i]
        version_anterior = version_actual.prev_record
        if version_anterior:
            delta = version_actual.diff_against(version_anterior)
            version_actual.cambios_calculados = delta.changes

    contexto = {
        'historial': historial
    }
    return render(request, 'control/config/historial_categorias_alergia.html', contexto)


@login_required
@rol_requerido(['Administrador'])
def reportes(request):
    # Obtenemos todos los profesionales y el que está actualmente como encargado
    profesionales_todos = Profesional.objects.select_related('usuario').all()
    encargados_actuales = profesionales_todos.filter(encargado=True)
    # Profesionales que aún no son encargados, para el selector de "agregar"
    profesionales_no_encargados = profesionales_todos.filter(encargado=False)

    if request.method == 'POST':
        action = request.POST.get('action')

        # --- ACCIÓN: Agregar uno o más profesionales encargados ---
        if action == 'agregar_encargados':
            nuevos_encargados_ruts = request.POST.getlist('profesionales_a_agregar')
            if not nuevos_encargados_ruts:
                messages.warning(request, 'No se seleccionó ningún profesional para agregar.')
            else:
                try:
                    profesionales_a_actualizar = Profesional.objects.filter(rut__in=nuevos_encargados_ruts)
                    count = profesionales_a_actualizar.update(encargado=True)
                    messages.success(request, f'Se agregaron {count} nuevos encargados de reportes.')
                except Exception as e:
                    messages.error(request, f'Ocurrió un error al agregar encargados: {e}')
            return redirect('control:reportes')

        # --- ACCIÓN: Remover un profesional encargado ---
        elif action == 'remover_encargado':
            encargado_a_remover_rut = request.POST.get('encargado_rut')
            try:
                profesional = get_object_or_404(Profesional, rut=encargado_a_remover_rut)
                profesional.encargado = False
                profesional.save()
                messages.info(request, f'Se ha removido a {profesional.nombre_completo} de la lista de encargados.')
            except Profesional.DoesNotExist:
                messages.error(request, 'El profesional seleccionado no existe.')
            except Exception as e:
                messages.error(request, f'Ocurrió un error al remover al encargado: {e}')
            return redirect('control:reportes')

        # --- ACCIÓN: Enviar el reporte por correo ---
        elif action == 'enviar_reporte':
            if not encargados_actuales.exists():
                messages.error(request, 'No se puede enviar el reporte porque no hay un profesional encargado asignado.')
                return redirect('control:reportes')

            # Buscamos los niños con controles atrasados
            controles_atrasados = Control.objects.filter(
                fecha_realizacion_control__isnull=True,
                deshabilitado=False, # Añadido para no reportar los deshabilitados
                fecha_control_programada__lt=date.today() - timedelta(days=7) # Atrasados por más de 7 días
            ).select_related('nino').order_by('nino__ap_paterno', 'nino__nombre')

            # --- Construcción del mensaje del correo directamente en la vista ---
            fecha_reporte = date.today().strftime("%d/%m/%Y")
            asunto = f'Reporte de Controles Atrasados - {fecha_reporte}'
            destinatarios = [enc.email for enc in encargados_actuales]

            # Usamos un template para el cuerpo del correo para mayor flexibilidad
            mensaje_html = render_to_string('control/reportes_mail/cuerpo_reporte_mail.html', {
                'controles_atrasados': controles_atrasados,
                'fecha_reporte': fecha_reporte,
            })
            """
            mensaje_body = (
                f'Estimado/a {encargado_actual.nombre_completo},\n\n'
                f'A continuación se presenta el listado de niños y niñas con controles de salud pendientes al {fecha_reporte}.\n\n'
            )

            if controles_atrasados.exists():
                mensaje_body += "--------------------------------------------------\n"
                for control in controles_atrasados:
                    mensaje_body += (
                        f"  - Niño/a: {control.nino.nombre} {control.nino.ap_paterno} {control.nino.ap_materno}\n"
                        f"  - RUT: {control.nino.rut_nino}\n"
                        f"  - Control: {control.nombre_control}\n"
                        f"  - Fecha Programada: {control.fecha_control_programada.strftime('%d/%m/%Y')}\n"
                        "--------------------------------------------------\n"
                    )
            else:
                mensaje_body += "¡Buenas noticias! No hay controles atrasados para reportar en este momento.\n\n"

            mensaje_body += "\nAtentamente,\nSistema de Gestión CESFAM."
            """
            try:
                send_mail(
                    subject=asunto,
                    message="Este es un correo HTML. Si no puede verlo, por favor active la vista HTML en su cliente de correo.", # Mensaje plano alternativo
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=destinatarios,
                    html_message=mensaje_html, # Usamos el mensaje en formato HTML
                )
                messages.success(request, f'Reporte enviado exitosamente a {len(destinatarios)} encargado(s).')
            except Exception as e:
                messages.error(request, f'Error al enviar el correo: {e}')
            
            return redirect('control:reportes')

    contexto = {
        'profesionales_no_encargados': profesionales_no_encargados,
        'encargados_actuales': encargados_actuales
    }
    return render(request, 'control/reportes_mail/enviar_reporte.html', contexto)