# script_poblacion_datos.py
import os
import django

# Inicializar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conidi.settings')
django.setup()

from login.models import TipoUsuario

# --- POBLAR ROLES ---
roles = [
    {"nombre": "Administrador", "descripcion": "Gestión total del sistema"},
    {"nombre": "Profesional", "descripcion": "Médicos o enfermeras"},
    {"nombre": "Tutor", "descripcion": "Apoderados responsables"},
]

for r in roles:
    obj, created = TipoUsuario.objects.get_or_create(
        nombre=r["nombre"],
        defaults={"descripcion": r["descripcion"]}
    )
    if created:
        print(f"Rol {r['nombre']} creado")
    else:
        print(f"Rol {r['nombre']} ya existía")