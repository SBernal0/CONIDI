# control/management/commands/enviar_alertas_controles.py

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import date, timedelta

from control.models import Control
from login.models import NinoTutor

class Command(BaseCommand):
    help = 'Envía notificaciones por correo a los tutores sobre controles que han pasado a estado atrasado.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Iniciando la tarea de envío de alertas de controles...'))

        hoy = date.today()

        # 1. Buscamos controles que cumplan las siguientes condiciones:
        #    - Aún no se han realizado.
        #    - La notificación de alerta NO ha sido enviada.
        #    - La fecha de hoy ya superó la fecha programada del control.
        controles_pendientes = Control.objects.filter(
            fecha_realizacion_control__isnull=True,
            notificacion_enviada=False,
            fecha_control_programada__lt=hoy
        ).select_related('nino', 'periodo')

        if not controles_pendientes.exists():
            self.stdout.write(self.style.SUCCESS('No hay nuevos controles atrasados para notificar hoy.'))
            return

        self.stdout.write(f'Se encontraron {controles_pendientes.count()} controles atrasados para notificar.')

        controles_notificados_ids = []

        # 2. Iteramos sobre cada control encontrado
        for control in controles_pendientes:
            nino = control.nino
            
            # 3. Buscamos todos los tutores asociados a ese niño
            relaciones = NinoTutor.objects.filter(nino=nino).select_related('tutor')

            if not relaciones:
                self.stdout.write(self.style.WARNING(f'El niño {nino} no tiene tutores asignados. No se puede notificar.'))
                continue

            for relacion in relaciones:
                tutor = relacion.tutor
                if tutor.email:
                    # 4. Preparamos y enviamos el correo electrónico
                    asunto = f'Alerta de Control Atrasado para {nino.nombre}'
                    mensaje = (
                        f'Estimado/a {tutor.nombre_completo},\n\n'
                        f'Le informamos que el control de salud "{control.nombre_control}" de {nino.nombre} {nino.ap_paterno}, '
                        f'que estaba programado para el {control.fecha_control_programada.strftime("%d/%m/%Y")}, se encuentra atrasado.\n\n'
                        'Por favor, acérquese al CESFAM para reagendar o realizar el control lo antes posible.\n\n'
                        'Atentamente,\n'
                        'Equipo CESFAM'
                    )
                    
                    try:
                        send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [tutor.email])
                        self.stdout.write(self.style.SUCCESS(f'Correo enviado a {tutor.email} para el control de {nino.nombre}.'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error al enviar correo a {tutor.email}: {e}'))

                else:
                    self.stdout.write(self.style.WARNING(f'El tutor {tutor.nombre_completo} no tiene email. No se puede notificar.'))
            
            # Agregamos el ID del control a una lista para actualizarlo después
            controles_notificados_ids.append(control.id)

        # 5. Actualizamos todos los controles notificados en una sola consulta
        if controles_notificados_ids:
            Control.objects.filter(id__in=controles_notificados_ids).update(notificacion_enviada=True)
            self.stdout.write(self.style.NOTICE(f'Se marcaron {len(controles_notificados_ids)} controles como notificados.'))

        self.stdout.write(self.style.SUCCESS('Tarea de envío de alertas finalizada.'))