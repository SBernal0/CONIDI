# control/management/commands/run_scheduler.py

import logging
import time
from django.core.management.base import BaseCommand
from apscheduler.schedulers.blocking import BlockingScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.conf import settings

from control.scheduler import enviar_alertas_job


class Command(BaseCommand):
    help = "Inicia el planificador de tareas APScheduler en modo de bloqueo."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)

        # --- CONFIGURACIÓN DE LOGGING COMPATIBLE CON DJANGO ---
        # Esto asegura que nuestros mensajes se muestren en la consola.
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Usamos un bloque try...finally para garantizar que shutdown() se llame siempre.
        # Esto es más robusto que el manejo de señales, especialmente en Windows.
        try:
            # Añadimos un pequeño retraso para evitar conflictos con la BD al iniciar
            logging.info("Esperando 5 segundos antes de iniciar el planificador...")
            time.sleep(5)
            
            scheduler.add_jobstore(DjangoJobStore(), "default")
            scheduler.add_job(
                enviar_alertas_job, 'cron', hour=2, minute=31, # Hora de ejecución
                id='enviar_alertas_diarias', replace_existing=True
            )
            logging.info("Tarea añadida. Iniciando el planificador... (Presiona Ctrl+C para detener)")
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logging.info("Señal de apagado recibida.")
        finally: # Este bloque se ejecutará siempre, incluso si hay un error.
            logging.info("Apagando el planificador...")
            if scheduler.running:
                # El parámetro wait=False es crucial para evitar que se quede pegado
                # si hay tareas en ejecución o problemas con la base de datos.
                scheduler.shutdown(wait=False)
            logging.info("Planificador detenido.")