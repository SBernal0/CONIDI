import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conidi.settings')
django.setup()

from control.models import CategoriaAlergia

print("Poblando categorías de alergia...")

categorias = [
    'Alimentaria', 'Cutánea (Dermatológica)', 'Respiratoria',
    'Picadura de Insecto', 'Fármacos', 'Contacto (ej. látex)', 'Otra'
]

for nombre_cat in categorias:
    cat, created = CategoriaAlergia.objects.get_or_create(nombre=nombre_cat)
    if created:
        print(f' -> Creada categoría: {cat.nombre}')

print("\n¡Población de categorías completada!")