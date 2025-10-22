# control/scheduler.py

from django.core.management import call_command
import logging
from io import StringIO

logger = logging.getLogger(__name__)

def enviar_alertas_job():
    logger.info("Scheduler: Iniciando la ejecución de la tarea 'enviar_alertas_job'.")
    try:
        # Capturamos la salida del comando para que aparezca en el log del scheduler
        stdout_buffer = StringIO()
        stderr_buffer = StringIO()
        call_command('enviar_alertas_controles', stdout=stdout_buffer, stderr=stderr_buffer)
        
        logger.info(f"Scheduler: Salida del comando 'enviar_alertas_controles':\n{stdout_buffer.getvalue()}")
        if stderr_buffer.getvalue():
            logger.error(f"Scheduler: Errores del comando 'enviar_alertas_controles':\n{stderr_buffer.getvalue()}")
        logger.info("Scheduler: Tarea 'enviar_alertas_job' completada.")
    except Exception as e:
        logger.error(f"Scheduler: Error inesperado al ejecutar 'enviar_alertas_job': {e}", exc_info=True)