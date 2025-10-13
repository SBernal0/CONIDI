# control/management/commands/recalcular_controles.py

from django.core.management.base import BaseCommand
from control.models import Nino, Control, PeriodoControl
from dateutil.relativedelta import relativedelta

class Command(BaseCommand):
    help = 'Limpia y regenera todos los controles pendientes, respetando los que ya fueron realizados.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Iniciando recálculo (versión final) de calendarios...'))

        # PASO 1: Borrar TODOS los controles PENDIENTES en una sola operación.
        controles_borrados, _ = Control.objects.filter(fecha_realizacion_control__isnull=True).delete()
        self.stdout.write(self.style.SUCCESS(f'-> {controles_borrados} controles pendientes eliminados para empezar de cero.'))

        # PASO 2: Obtener las reglas, los niños y, crucialmente, los controles YA REALIZADOS.
        periodos_actuales = PeriodoControl.objects.all()
        ninos = Nino.objects.all()
        
        # Creamos un conjunto de tuplas (nino_id, periodo_id) para una búsqueda ultra-rápida.
        # Esto contiene la "lista de excepciones" de los controles que no debemos volver a crear.
        controles_realizados = set(
            Control.objects.filter(fecha_realizacion_control__isnull=False)
            .values_list('nino_id', 'periodo_id')
        )
        self.stdout.write(f'-> Se encontraron {len(controles_realizados)} controles ya realizados que se respetarán.')

        # PASO 3: Preparamos la lista para crear solo los controles necesarios.
        controles_a_crear = []
        for nino in ninos:
            for periodo in periodos_actuales:
                # LA LÓGICA CLAVE: Verificamos si este niño ya tiene este periodo realizado.
                if (nino.pk, periodo.pk) not in controles_realizados:
                    # Si no está en la lista de excepciones, lo añadimos para su creación.
                    fecha_programada = nino.fecha_nacimiento + relativedelta(months=periodo.mes_control)
                    controles_a_crear.append(
                        Control(
                            nino=nino,
                            periodo=periodo,
                            nombre_control=periodo.nombre_mes_control,
                            fecha_control_programada=fecha_programada,
                            estado_control="Pendiente"
                        )
                    )
        
        # PASO 4: Creamos todos los nuevos controles en una sola operación.
        if controles_a_crear:
            Control.objects.bulk_create(controles_a_crear)
            self.stdout.write(self.style.SUCCESS(f'-> {len(controles_a_crear)} nuevos controles pendientes creados.'))
        else:
            self.stdout.write(self.style.SUCCESS('-> No fue necesario crear nuevos controles pendientes.'))
        
        self.stdout.write(self.style.SUCCESS('\n¡Recálculo completado!'))