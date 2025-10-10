import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conidi.settings')
django.setup()

from control.models import Nino

datos_ninos = [
    {"nombre": "Benjamín", "fecha_nacimiento": "2025-08-07", "rut": "99999999-9"},
]

for datos in datos_ninos:
    Nino.objects.get_or_create(**datos)

print("Niños creados correctamente.")
