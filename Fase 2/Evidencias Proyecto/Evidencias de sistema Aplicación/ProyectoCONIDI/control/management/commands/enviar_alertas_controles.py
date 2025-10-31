# control/management/commands/enviar_alertas_controles.py

from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives # Changed from send_mail
from django.template.loader import render_to_string # New import
from django.conf import settings
from django.utils import timezone
from datetime import date, timedelta
from collections import defaultdict # New import for grouping

from control.models import Control
from login.models import NinoTutor, Tutor # Added Tutor import


class Command(BaseCommand):
    help = 'Envía notificaciones por correo a los tutores sobre controles que han pasado a estado atrasado.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Iniciando la tarea de envío de alertas de controles...'))

        hoy = date.today()

        # 1. Identificar todos los controles atrasados que aún no han sido notificados
        # y que tienen un niño asociado.
        # Filtramos por controles que están atrasados (fecha programada < hoy)
        # y que no han sido deshabilitados.
        # También nos aseguramos de que el control no haya sido realizado y que la notificación no se haya enviado.
        controles_atrasados_pendientes_notificar = Control.objects.filter(
            fecha_realizacion_control__isnull=True,
            deshabilitado=False,
            notificacion_enviada=False,
            fecha_control_programada__lt=hoy
).select_related('nino', 'periodo').order_by('nino__ap_paterno', 'nino__nombre', 'fecha_control_programada')

        if not controles_atrasados_pendientes_notificar.exists():
            self.stdout.write(self.style.SUCCESS('No hay nuevos controles atrasados para notificar hoy.'))
            return

        self.stdout.write(f'Se encontraron {controles_atrasados_pendientes_notificar.count()} controles atrasados que requieren notificación.')

        # Diccionario para agrupar los controles por tutor
        # {tutor_email: {'tutor_obj': Tutor, 'children_data': {nino_rut: {'nino_obj': Nino, 'controles': [Control, ...]}}}}
        tutors_to_notify = defaultdict(lambda: {'tutor_obj': None, 'children_data': defaultdict(lambda: {'nino_obj': None, 'controles': []})})
        
        all_notified_control_ids = [] # Para marcar todos los controles como notificados al final

        # 2. Agrupar los controles atrasados por tutor
        for control in controles_atrasados_pendientes_notificar:
            nino = control.nino
            
            # Obtener todos los tutores asociados a este niño
            relaciones_nino_tutor = NinoTutor.objects.filter(nino=nino).select_related('tutor')

            if not relaciones_nino_tutor.exists():
                self.stdout.write(self.style.WARNING(f'El niño {nino.nombre_completo} (RUT: {nino.rut_nino}) no tiene tutores asignados. No se puede notificar sobre su control "{control.nombre_control}".'))
                continue

            for relacion in relaciones_nino_tutor:
                tutor = relacion.tutor
                if tutor and tutor.email:
                    tutors_to_notify[tutor.email]['tutor_obj'] = tutor
                    tutors_to_notify[tutor.email]['children_data'][nino.rut_nino]['nino_obj'] = nino
                    tutors_to_notify[tutor.email]['children_data'][nino.rut_nino]['controles'].append(control)
                    all_notified_control_ids.append(control.id)
                else:
                    self.stdout.write(self.style.WARNING(f'El tutor {tutor.nombre_completo if tutor else "N/A"} (RUT: {tutor.rut if tutor else "N/A"}) asociado a {nino.nombre_completo} no tiene email o no existe. No se puede notificar.'))

        # 3. Enviar un correo consolidado a cada tutor
        for tutor_email, data in tutors_to_notify.items():
            tutor = data['tutor_obj']
            children_data = data['children_data'] # This is a defaultdict, convert to list of dicts for template
            
            # Convertir children_data a un formato más amigable para la plantilla
            children_for_template = []
            for nino_rut, nino_info in children_data.items():
                children_for_template.append({
                    'nino_obj': nino_info['nino_obj'],
                    'controles': sorted(nino_info['controles'], key=lambda c: c.fecha_control_programada)
                })
            
            # Ordenar los niños por apellido paterno para el email
            children_for_template.sort(key=lambda x: x['nino_obj'].ap_paterno)

            asunto = f'Alerta Importante: Controles de Salud Atrasados de sus Hijos/as'
            
            # Renderizar el cuerpo del correo desde una plantilla HTML
            mensaje_html = render_to_string('control/reportes_mail/email_alerta_controles_consolidados.html', {
                'tutor_nombre': tutor.nombre_completo,
                'children_data': children_for_template, # Pass the structured data
                'fecha_reporte': hoy.strftime("%d/%m/%Y"),
            })

            # Usar EmailMultiAlternatives para enviar HTML
            email = EmailMultiAlternatives(
                subject=asunto,
                body="Este es un correo HTML. Si no puede verlo, por favor active la vista HTML en su cliente de correo.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[tutor_email]
            )
            email.attach_alternative(mensaje_html, "text/html")

            try:
                email.send()
                self.stdout.write(self.style.SUCCESS(f'Correo consolidado enviado a {tutor_email} para {len(children_for_template)} niño(s).'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error al enviar correo consolidado a {tutor_email}: {e}'))

        # 4. Actualizar todos los controles que fueron incluidos en alguna notificación
        if all_notified_control_ids:
            # Usamos set para eliminar duplicados si un control fue asociado a múltiples tutores
            Control.objects.filter(id__in=list(set(all_notified_control_ids))).update(notificacion_enviada=True)
            self.stdout.write(self.style.NOTICE(f'Se marcaron {len(set(all_notified_control_ids))} controles como notificados.'))

                    
        self.stdout.write(self.style.SUCCESS('Tarea de envío de alertas consolidadas finalizada.'))
