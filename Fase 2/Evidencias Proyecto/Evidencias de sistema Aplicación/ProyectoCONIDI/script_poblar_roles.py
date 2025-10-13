# script_poblar_roles.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conidi.settings')
django.setup()

from login.models import Rol # <- CAMBIO: Importamos Rol

print("Poblando roles...")

roles = [
    {"nombre": "Administrador", "descripcion": "Gestión total del sistema."},
    {"nombre": "Profesional", "descripcion": "Personal de salud (médicos, enfermeras, etc.)."},
    {"nombre": "Tutor", "descripcion": "Apoderados o responsables de los niños."},
]

for r_data in roles:
    # CAMBIO: Usamos el modelo Rol y el campo 'nombre_rol'
    rol, created = Rol.objects.get_or_create(
        nombre_rol=r_data["nombre"],
        defaults={"descripcion": r_data["descripcion"]}
    )
    if created:
        print(f"-> Rol '{rol.nombre_rol}' creado.")
    else:
        print(f"-> Rol '{rol.nombre_rol}' ya existía.")

print("\n¡Población de roles completada!")