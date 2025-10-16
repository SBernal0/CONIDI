# control/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from dateutil.relativedelta import relativedelta

# Importamos todos los modelos que vamos a necesitar
from .models import Nino, Control, PeriodoControl, Vacuna, VacunaAplicada

@receiver(post_save, sender=Nino)
def crear_calendario_controles(sender, instance, created, **kwargs):
    """
    Esta función se ejecuta cuando se guarda un Nino.
    Si es nuevo (created=True), genera su calendario de controles.
    """
    if created:
        print(f"Nuevo niño detectado: {instance.nombre}. Generando calendario de controles...")
        todos_los_periodos = PeriodoControl.objects.all()

        for periodo in todos_los_periodos:
            fecha_programada = instance.fecha_nacimiento + relativedelta(months=periodo.mes_control)
            
            Control.objects.create(
                nino=instance,
                periodo=periodo,
                nombre_control=periodo.nombre_mes_control,
                fecha_control_programada=fecha_programada,
                estado_control="Pendiente"
            )
        print(f"Calendario de controles para {instance.nombre} generado.")


@receiver(post_save, sender=Nino)
def crear_calendario_vacunacion(sender, instance, created, **kwargs):
    """
    Esta función también se ejecuta cuando se guarda un Nino.
    Si es nuevo (created=True), genera su calendario de vacunación. 💉
    """
    if created:
        print(f"Generando calendario de vacunación para {instance.nombre}...")
        # Obtenemos solo las vacunas que tienen un mes de aplicación definido
        vacunas_programadas = Vacuna.objects.filter(meses_programada__isnull=False)

        for vacuna in vacunas_programadas:
            fecha_programada = instance.fecha_nacimiento + relativedelta(months=vacuna.meses_programada)

            # Creamos el registro de 'VacunaAplicada' como pendiente
            VacunaAplicada.objects.create(
                nino=instance,
                vacuna=vacuna,
                fecha_programada=fecha_programada
                # Los demás campos (fecha_aplicacion, dosis, etc.) se quedan vacíos por defecto
            )
        print(f"Calendario de vacunación para {instance.nombre} generado.")