# control/management/commands/run_scheduler.py


import logging
import signal
import time
from django.core.management.base import BaseCommand
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.utils import timezone

from control.scheduler import enviar_alertas_job


class Command(BaseCommand):
    help = "Inicia el planificador de tareas APScheduler en modo de bloqueo."

    def handle(self, *args, **options):
        
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        
        logging.basicConfig(
            level=logging.INFO, format='%(levelname)s: %(message)s', force=True
        )

        def shutdown_handler(signum, frame):
            logging.info("Señal de apagado (Ctrl+C) recibida. Deteniendo el planificador...")

            if scheduler.running:
                scheduler.shutdown(wait=False)
        
        signal.signal(signal.SIGINT, shutdown_handler)

        try:
            logging.info("Esperando 5 segundos antes de iniciar el planificador...")
            time.sleep(5)
            
            
            scheduler.add_job(
                enviar_alertas_job, 
                'cron', 
                # Define aquí la hora y el minuto para la ejecución diaria.
                # Formato 24 horas (hora: 0-23, minuto: 0-59).
                hour=0,    # <-- Cambia este valor por la hora deseada (ej: 2 para las 2 AM)
                minute=17, # <-- Cambia este valor por el minuto deseado (ej: 30)
                id='enviar_alertas_diarias', replace_existing=True
            )
            logging.info("Tarea añadida. Iniciando el planificador... (Presiona Ctrl+C para detener)")
            
            scheduler.start()

            logging.info(f"Scheduler configurado con zona horaria: {scheduler.timezone}")
            scheduler.print_jobs()

            while scheduler.running:
                time.sleep(1)

        except Exception as e:
            logging.error(f"Error inesperado en el planificador: {e}", exc_info=True)
        finally:
            if scheduler.running:
                scheduler.shutdown(wait=False)
            logging.info("Planificador detenido. Proceso finalizado.")