from django.db.models.signals import post_save
from django.dispatch import receiver
from dateutil.relativedelta import relativedelta

from .models import Nino, Control, PeriodoControl

@receiver(post_save, sender=Nino)
def crear_calendario_controles(sender, instance, created, **kwargs):
    """
    Esta función se ejecuta cada vez que un objeto Nino es guardado.
    Si el objeto es nuevo (created=True), genera su calendario de controles.
    """
    if created:
        print(f"Nuevo niño detectado: {instance.nombre}. Generando calendario de controles...")
        todos_los_periodos = PeriodoControl.objects.all()

        for periodo in todos_los_periodos:
            fecha_programada = instance.fecha_nacimiento + relativedelta(months=periodo.mes_control)

            # Creamos el control futuro en la base de datos
            Control.objects.create(
                nino=instance,
                periodo=periodo, # <-- Guarda la relación con el periodo
                nombre_control=periodo.nombre_mes_control,
                fecha_control_programada=fecha_programada,
                estado_control="Pendiente"
            )
        print(f"Calendario para {instance.nombre} generado con éxito.")