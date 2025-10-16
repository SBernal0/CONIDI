import os
import django

# --- Configuración de Django ---
# Le dice al script dónde encontrar la configuración de tu proyecto.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conidi.settings')
# Carga esa configuración e inicializa Django.
django.setup()
# ------------------------------------

from control.models import Vacuna

def poblar_vacunas_minsal():
    """
    Puebla la tabla Vacuna con el calendario estándar del MINSAL Chile
    para el programa de inmunización infantil.
    """
    print("Poblando vacunas estándar con calendario MINSAL...")
    
    # Formato: (edad_en_meses, nombre_de_la_vacuna)
    calendario_vacunas = [
        # Recién Nacido
        (0, 'BCG'),
        (0, 'Hepatitis B (Recién Nacido)'),
        
        # 2 Meses
        (2, 'Hexavalente (1ª Dosis)'),
        (2, 'Neumocócica Conjugada (1ª Dosis)'),
        (2, 'Rotavirus (1ª Dosis)'),
        
        # 4 Meses
        (4, 'Hexavalente (2ª Dosis)'),
        (4, 'Neumocócica Conjugada (2ª Dosis)'),
        (4, 'Rotavirus (2ª Dosis)'),
        
        # 6 Meses
        (6, 'Hexavalente (3ª Dosis)'),
        (6, 'Neumocócica Conjugada (3ª Dosis)'),
        (6, 'Rotavirus (3ª Dosis)'),
        
        # 12 Meses (1 año)
        (12, 'Tres Vírica (SRP) (1ª Dosis)'),
        (12, 'Neumocócica Conjugada (Refuerzo)'),
        (12, 'Meningocócica Conjugada'),
        
        # 18 Meses (1 año y medio)
        (18, 'Hexavalente (4ª Dosis - Refuerzo)'),
        (18, 'Hepatitis A'),
        (18, 'Varicela'),
        
        # 36 Meses (3 años)
        (36, 'Tres Vírica (SRP) (2ª Dosis)'),
        
        # Kinder (Aproximadamente 60 meses / 5 años)
        (60, 'DTPa (Refuerzo)'),
        
        # Vacunas estacionales o fuera del calendario inicial
        (None, 'Influenza (Anual)'),
    ]

    for meses, nombre in calendario_vacunas:
        # Busca una vacuna con ese nombre. Si la encuentra, la actualiza. Si no, la crea.
        vacuna, created = Vacuna.objects.update_or_create(
            nom_vacuna=nombre,
            defaults={'meses_programada': meses}
        )
        
        if created:
            if meses is not None:
                print(f' -> Creada: {vacuna.nom_vacuna} (a los {meses} meses)')
            else:
                print(f' -> Creada: {vacuna.nom_vacuna} (sin mes fijo)')
        else:
            # Si ya existía, confirmamos que se actualizó
            print(f' -> Verificada/Actualizada: {vacuna.nom_vacuna}')

# --- Llamada a la función ---
poblar_vacunas_minsal()

print("\n¡Población de vacunas del calendario MINSAL completada!")