import os
import django
from datetime import date, timedelta
import random
from faker import Faker # Importamos Faker

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conidi.settings')
django.setup()

# --- IMPORTACIONES ---
from control.models import Region, Ciudad, Comuna, Nino
from login.models import Tutor, NinoTutor

# --- Inicializar Faker (en español chileno) ---
fake = Faker('es_CL')

# --- Helper para generar RUTs chilenos válidos (aproximado) ---
def calcular_dv(rut_sin_dv):
    rut_reverso = str(rut_sin_dv)[::-1]
    multiplicador = 2
    suma = 0
    for digito in rut_reverso:
        suma += int(digito) * multiplicador
        multiplicador += 1
        if multiplicador == 8:
            multiplicador = 2
    resto = suma % 11
    dv = 11 - resto
    if dv == 11:
        return '0'
    elif dv == 10:
        return 'K'
    else:
        return str(dv)

def generar_rut_fake():
    numero_base = random.randint(5000000, 30000000) # Rango amplio de RUTs
    dv = calcular_dv(numero_base)
    return f"{numero_base}-{dv}"

print("Poblando la base de datos con 100 niños (0-12 años) y 60 tutores...")

# --- 1. Crear datos geográficos de ejemplo ---
region_obj, _ = Region.objects.get_or_create(nom_region='Biobío')
ciudad_obj, _ = Ciudad.objects.get_or_create(nom_ciudad='Concepción', region=region_obj)
comuna_obj, _ = Comuna.objects.get_or_create(nom_comuna='Hualpén', ciudad=ciudad_obj)
print(f"-> Datos geográficos para '{comuna_obj.nom_comuna}' asegurados.")

# --- 2. Crear 60 perfiles de Tutor ---
print("\nGenerando 60 perfiles de Tutores...")
tutores_creados = []
for i in range(60):
    rut_tutor = generar_rut_fake()
    nombre_tutor = fake.name()
    # Generamos email falso
    email_tutor = f"{nombre_tutor.lower().replace(' ', '.').replace('..', '.')}{random.randint(1,100)}@mailfalso.cl"
    
    tutor_data = {
        'nombre_completo': nombre_tutor,
        'email': email_tutor,
        'telefono': fake.phone_number(),
        'direccion': fake.address(),
    }
    tutor_obj, created = Tutor.objects.get_or_create(rut=rut_tutor, defaults=tutor_data)
    tutores_creados.append(tutor_obj)

print(f"-> {len(tutores_creados)} perfiles de tutores asegurados.")

# --- 3. Crear 100 Niños de ejemplo (0 a 12 años) ---
print("\nGenerando 100 perfiles de Niños...")
ninos_creados = []
parentescos_posibles = [choice[0] for choice in NinoTutor.PARENTESCO_CHOICES]
sectores_disponibles = ['Sector Azul', 'Sector Verde', 'Sector Rojo', 'Sector Amarillo']

for i in range(100):
    rut_nino = generar_rut_fake()
    # Rango de edad de 0 a 12 años (144 meses)
    fecha_nacimiento_nino = date.today() - timedelta(days=random.randint(10, 365 * 12))
    sexo_nino = random.choice(['Masculino', 'Femenino'])
    
    if sexo_nino == 'Masculino':
        nombre_nino = fake.first_name_male()
    else:
        nombre_nino = fake.first_name_female()
    
    nino_data = {
        'nombre': nombre_nino,
        'ap_paterno': fake.last_name(),
        'ap_materno': fake.last_name(),
        'fecha_nacimiento': fecha_nacimiento_nino,
        'sexo': sexo_nino,
        'direccion': fake.address(),
        'comuna': comuna_obj,
        'sector': random.choice(sectores_disponibles), # Asigna un sector aleatorio
        'estado_seguimiento': 'ACTIVO' # Por defecto activos
    }
    
    nino_obj, created = Nino.objects.get_or_create(rut_nino=rut_nino, defaults=nino_data)
    
    if created:
        ninos_creados.append(nino_obj)
        # --- 4. Relacionar al Niño con un Tutor aleatorio ---
        tutor_aleatorio = random.choice(tutores_creados)
        parentesco_aleatorio = random.choice(parentescos_posibles)
        
        relacion, created_rel = NinoTutor.objects.get_or_create(
            nino=nino_obj,
            tutor=tutor_aleatorio,
            defaults={'parentesco': parentesco_aleatorio}
        )

print(f"-> {len(ninos_creados)} niños nuevos creados y relacionados.")
print("\n¡Población de entidades de ejemplo completada!")