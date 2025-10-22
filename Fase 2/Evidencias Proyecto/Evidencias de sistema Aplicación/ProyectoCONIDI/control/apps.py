# control/apps.py

from django.apps import AppConfig

class ControlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'control'
    verbose_name = "Control de Niños"

    def ready(self):
        # Importamos las señales para que se registren.
        import control.signals