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
        # Usamos la zona horaria local del sistema para que la hora programada
        # coincida con el reloj del servidor. Asegúrate que settings.TIME_ZONE
        # esté configurado a tu zona horaria local (ej. 'America/Santiago').
        # CAMBIO: Usamos BackgroundScheduler para una mejor integración.
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        
        # --- CONFIGURACIÓN DE LOGGING COMPATIBLE CON DJANGO ---
        # Esto asegura que nuestros mensajes se muestren en la consola.
        # El parámetro 'force=True' reinicia cualquier configuración de logging existente,
        # asegurando que nuestro formato sea el que se utilice.
        logging.basicConfig(
            level=logging.INFO, format='%(levelname)s: %(message)s', force=True
        )

        # --- MANEJADOR DE SEÑALES PARA UN APAGADO ROBUSTO ---
        # Registramos una función para que se ejecute cuando se presione Ctrl+C (señal SIGINT).
        def shutdown_handler(signum, frame):
            logging.info("Señal de apagado (Ctrl+C) recibida. Deteniendo el planificador...")
            # En lugar de llamar a shutdown() directamente, cambiamos el estado del scheduler.
            # El bucle principal se encargará del apagado.
            if scheduler.running:
                scheduler.shutdown(wait=False)
        
        signal.signal(signal.SIGINT, shutdown_handler)

        # Usamos un bloque try...finally para garantizar que shutdown() se llame siempre.
        # Esto es más robusto que el manejo de señales, especialmente en Windows.
        try:
            # Añadimos un pequeño retraso para evitar conflictos con la BD al iniciar
            logging.info("Esperando 5 segundos antes de iniciar el planificador...")
            time.sleep(5)
            
            # No es necesario añadir el jobstore manualmente con BackgroundScheduler
            # Django-apscheduler lo maneja si está en INSTALLED_APPS.

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
            
            # Iniciamos el planificador. Al ser un BackgroundScheduler, no bloqueará.
            scheduler.start()

            # Ahora que el scheduler está corriendo, podemos obtener la próxima hora de ejecución.
            logging.info(f"Scheduler configurado con zona horaria: {scheduler.timezone}")
            scheduler.print_jobs()

            # Mantenemos el script principal vivo con un bucle.
            while scheduler.running:
                time.sleep(1)

        except Exception as e:
            # Capturamos cualquier otro error inesperado durante la ejecución.
            logging.error(f"Error inesperado en el planificador: {e}", exc_info=True)
        finally:
            if scheduler.running:
                scheduler.shutdown(wait=False)
            logging.info("Planificador detenido. Proceso finalizado.")