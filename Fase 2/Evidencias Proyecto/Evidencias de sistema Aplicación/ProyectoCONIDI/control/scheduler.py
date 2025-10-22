# control/scheduler.py

import logging
from django.core.management import call_command

# Configura un logger para ver los mensajes del scheduler
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.INFO)

def enviar_alertas_job():
    """
    Función que será llamada por el scheduler.
    Ejecuta el comando de gestión para enviar las alertas.
    """
    logging.info("--- [Scheduler] Ejecutando la tarea programada: enviar_alertas_controles ---")
    try:
        call_command('enviar_alertas_controles.py')
        logging.info("--- [Scheduler] Tarea 'enviar_alertas_controles' finalizada exitosamente. ---")
    except Exception as e:
        logging.error(f"--- [Scheduler] Error al ejecutar la tarea: {e} ---", exc_info=True)