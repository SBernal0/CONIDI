# script_poblar_parametros.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conidi.settings')
django.setup()

from control.models import PeriodoControl

def poblar_periodos_control():
    print("Poblando hitos de PeriodoControl (0-9 años) con lista actualizada...")
    
    # Formato: (edad_en_meses, nombre_del_control)
    CONTROLES_ESTANDAR = [
        (0, "Control Díada"),
        (1, "CSI 1 mes"),
        (2, "CSI 2 meses"),
        (3, "CSI 3 meses"),
        (4, "CSI 4 meses"),
        (5, "Consulta Nutricional 5 meses"),
        (6, "CSI 6 meses"),
        (8, "CSI 8 meses"),
        (12, "CSI 12 meses (1 año)"),
        (18, "CSI 18 meses (1 año y medio)"),
        (24, "CSI 24 meses (2 años)"),
        (36, "CSI 36 meses (3 años)"),
        (42, "Consulta Nutricional 3 años y 6 meses"),
        (48, "CSI 48 meses (4 años)"),
        (60, "CSI 60 meses (5 años)"),
        (72, "CSI 72 meses (6 años)"),
        (84, "CSI 84 meses (7 años)"),
        (96, "CSI 96 meses (8 años)"),
        (108, "CSI 108 meses (9 años)"),
    ]

    # Usamos update_or_create para actualizar existentes y crear nuevos
    # Asignamos un margen de 30 días por defecto, puedes cambiarlo luego en la app
    for meses, nombre in CONTROLES_ESTANDAR:
        obj, created = PeriodoControl.objects.update_or_create(
            mes_control=meses,
            defaults={'nombre_mes_control': nombre, 'dias_margen': 30} 
        )
        if created:
            print(f"-> Creado: {nombre}")
        else:
            print(f"-> Actualizado/Verificado: {nombre}")

    print("\n¡Población de períodos de control completada!")

# --- Llamada a la función ---
poblar_periodos_control()