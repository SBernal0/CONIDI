from django.shortcuts import render, get_object_or_404
from datetime import date, timedelta
from .models import Nino

CONTROLES=[
    (0, "Recién nacido"),
    (1, "1 mes"),
    (2, "2 meses"),
    (4, "4 meses"),
    (6, "6 meses"),
    (12, "1 año"),
    (18, "1 año y medio"),
    (24, "2 años"),
    (36, "3 años"),
    (48, "4 años"),
    (60, "5 años"),
]

# Create your views here.
def controles(request, nino_id):
    nino = get_object_or_404(Nino, id=nino_id)
    hoy = date.today()
    edad_dias = (hoy - nino.fecha_nacimiento).days
    edad_meses = edad_dias // 30  # cálculo aproximado

    controles_calculados = []
    for meses, nombre_control in CONTROLES:
        fecha_control = nino.fecha_nacimiento + timedelta(days=meses * 30)
        realizado = fecha_control <= hoy
        controles_calculados.append({
            "nombre": nombre_control,
            "fecha_programada": fecha_control,
            "realizado": realizado
        })

    contexto = {
        "nino": nino,
        "controles": controles_calculados
    }
    return render(request, 'controles.html', context=contexto)