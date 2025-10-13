import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conidi.settings')
django.setup()

from control.models import PeriodoControl

CONTROLES_ESTANDAR = [
    (0, "Recién nacido"), (1, "1 mes"), (2, "2 meses"), (3, "3 meses"),
    (4, "4 meses"), (5, "5 meses"), (6, "6 meses"), (8, "8 meses"),
    (10, "10 meses"), (12, "12 meses (1 año)"), (15, "15 meses"),
    (18, "18 meses (1 año y medio)"), (21, "21 meses"),
    (24, "24 meses (2 años)"), (30, "30 meses"), (36, "36 meses (3 años)"),
    (48, "48 meses (4 años)"), (60, "60 meses (5 años)"),
]

print("Poblando hitos de PeriodoControl...")
for meses, nombre in CONTROLES_ESTANDAR:
    obj, created = PeriodoControl.objects.get_or_create(
        mes_control=meses,
        defaults={'nombre_mes_control': nombre}
    )
    if created:
        print(f"-> Creado: {nombre}")

print("\n¡Población de parámetros completada!")