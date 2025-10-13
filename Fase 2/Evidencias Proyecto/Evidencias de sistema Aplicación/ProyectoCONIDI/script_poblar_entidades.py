import os
import django
from datetime import date

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conidi.settings')
django.setup()

# --- IMPORTACIONES ACTUALIZADAS ---
from control.models import Region, Ciudad, Comuna, Nino
from login.models import Tutor, NinoTutor # Se añade NinoTutor

print("Poblando la base de datos con un conjunto de datos de prueba...")

# --- 1. Crear datos geográficos de ejemplo (sin cambios) ---
region_obj, _ = Region.objects.get_or_create(nom_region='Biobío')
ciudad_obj, _ = Ciudad.objects.get_or_create(nom_ciudad='Concepción', region=region_obj)
comuna_obj, _ = Comuna.objects.get_or_create(nom_comuna='Hualpén', ciudad=ciudad_obj)
print(f"-> Datos geográficos para '{comuna_obj.nom_comuna}' asegurados.")

# --- 2. Crear varios perfiles de Tutor (sin el campo 'parentesco') ---
tutores_data = [
    {'rut': '15888777-6', 'nombre_completo': 'Ana Rojas Villena', 'email': 'ana.rojas@email.com'},
    {'rut': '16111222-3', 'nombre_completo': 'Carlos González Soto', 'email': 'cgonzalez@email.com'},
    {'rut': '12333444-5', 'nombre_completo': 'Luisa Pérez Morales', 'email': 'luisa.perez@email.com'},
    {'rut': '17555666-K', 'nombre_completo': 'Javier Muñoz Tapia', 'email': 'jmunoz@email.com'},
]

tutores_creados = {}
for data in tutores_data:
    # El 'defaults' ya no incluye 'parentesco'
    tutor_obj, created = Tutor.objects.get_or_create(rut=data['rut'], defaults=data)
    tutores_creados[data['rut']] = tutor_obj
    if created:
        print(f"-> Perfil de Tutor para '{tutor_obj.nombre_completo}' creado.")
    else:
        print(f"-> Perfil de Tutor para '{tutor_obj.nombre_completo}' ya existía.")


# --- 3. Crear 10 Niños de ejemplo (con el campo 'parentesco' añadido a cada uno) ---
# La fecha actual es Octubre de 2025.
ninos_data = [
    # Edad: ~3 meses
    {'rut_nino': '30111222-3', 'nombre': 'Sofía', 'ap_paterno': 'González', 'ap_materno': 'Rojas', 'fecha_nacimiento': date(2025, 7, 15), 'sexo': 'Femenino', 'tutor_rut': '15888777-6', 'parentesco': 'Madre'},
    # Edad: ~1 año y 2 meses
    {'rut_nino': '29333444-5', 'nombre': 'Mateo', 'ap_paterno': 'González', 'ap_materno': 'Soto', 'fecha_nacimiento': date(2024, 8, 20), 'sexo': 'Masculino', 'tutor_rut': '16111222-3', 'parentesco': 'Padre'},
    # Edad: ~2 años y 1 mes
    {'rut_nino': '28555666-K', 'nombre': 'Isabella', 'ap_paterno': 'Muñoz', 'ap_materno': 'Pérez', 'fecha_nacimiento': date(2023, 9, 5), 'sexo': 'Femenino', 'tutor_rut': '12333444-5', 'parentesco': 'Madre'},
    # Edad: ~4 meses
    {'rut_nino': '30012345-6', 'nombre': 'Lucas', 'ap_paterno': 'González', 'ap_materno': 'Castro', 'fecha_nacimiento': date(2025, 6, 1), 'sexo': 'Masculino', 'tutor_rut': '16111222-3', 'parentesco': 'Padre'},
    # Edad: ~3 años
    {'rut_nino': '27123456-7', 'nombre': 'Emilia', 'ap_paterno': 'Muñoz', 'ap_materno': 'Pérez', 'fecha_nacimiento': date(2022, 10, 10), 'sexo': 'Femenino', 'tutor_rut': '12333444-5', 'parentesco': 'Madre'},
    # Edad: ~4 años y 6 meses
    {'rut_nino': '26987654-3', 'nombre': 'Benjamín', 'ap_paterno': 'Díaz', 'ap_materno': 'Silva', 'fecha_nacimiento': date(2021, 4, 30), 'sexo': 'Masculino', 'tutor_rut': '17555666-K', 'parentesco': 'Tutor legal'},
    # Edad: ~6 meses
    {'rut_nino': '29876543-2', 'nombre': 'Julieta', 'ap_paterno': 'Torres', 'ap_materno': 'Flores', 'fecha_nacimiento': date(2025, 4, 12), 'sexo': 'Femenino', 'tutor_rut': '15888777-6', 'parentesco': 'Tía'},
    # Edad: ~1 año y 8 meses
    {'rut_nino': '28765432-1', 'nombre': 'Agustín', 'ap_paterno': 'Vargas', 'ap_materno': 'Reyes', 'fecha_nacimiento': date(2024, 2, 22), 'sexo': 'Masculino', 'tutor_rut': '17555666-K', 'parentesco': 'Padre'},
    # Edad: ~2 años y 11 meses
    {'rut_nino': '27654321-0', 'nombre': 'Florencia', 'ap_paterno': 'Araya', 'ap_materno': 'López', 'fecha_nacimiento': date(2022, 11, 18), 'sexo': 'Femenino', 'tutor_rut': '12333444-5', 'parentesco': 'Abuela'},
    # Edad: ~4 años y 11 meses
    {'rut_nino': '26543210-K', 'nombre': 'Vicente', 'ap_paterno': 'Rojas', 'ap_materno': 'Mora', 'fecha_nacimiento': date(2020, 11, 25), 'sexo': 'Masculino', 'tutor_rut': '15888777-6', 'parentesco': 'Tío'},
]

for data in ninos_data:
    nino_obj, created = Nino.objects.get_or_create(
        rut_nino=data['rut_nino'],
        defaults={
            'nombre': data['nombre'],
            'ap_paterno': data['ap_paterno'],
            'ap_materno': data['ap_materno'],
            'fecha_nacimiento': data['fecha_nacimiento'],
            'sexo': data['sexo'],
            'direccion': 'Avenida Siempreviva 742',
            'comuna': comuna_obj
        }
    )

    if created:
        print(f"-> Niño '{nino_obj.nombre} {nino_obj.ap_paterno}' creado.")
    else:
        # Si el niño ya existía, lo obtenemos para asegurar que la relación se cree
        nino_obj = Nino.objects.get(rut_nino=data['rut_nino'])
        print(f"-> Niño '{nino_obj.nombre} {nino_obj.ap_paterno}' ya existía.")

    # --- 4. Relacionar al Niño con su Tutor (LÓGICA ACTUALIZADA) ---
    tutor_a_asignar = tutores_creados.get(data['tutor_rut'])
    if tutor_a_asignar:
        # Creamos el objeto de la relación directamente para poder especificar el parentesco
        relacion, created_rel = NinoTutor.objects.get_or_create(
            nino=nino_obj,
            tutor=tutor_a_asignar,
            defaults={'parentesco': data['parentesco']}
        )
        if created_rel:
            print(f"   -> Relación creada: '{tutor_a_asignar.nombre_completo}' es '{relacion.parentesco}' de '{nino_obj.nombre}'.")
        else:
            print(f"   -> Relación entre '{tutor_a_asignar.nombre_completo}' y '{nino_obj.nombre}' ya existía.")


print("\n¡Población de entidades de ejemplo completada!")