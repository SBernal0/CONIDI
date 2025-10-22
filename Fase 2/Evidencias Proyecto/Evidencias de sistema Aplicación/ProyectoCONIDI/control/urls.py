from django.urls import path
from . import views


urlpatterns = [
    # --- RUTAS ESPECÍFICAS PRIMERO ---
    path('controles/configuracion/', views.configurar_periodos, name='configurar_periodos'),
    path('controles/registrar/<int:control_id>/', views.registrar_control, name='registrar_control'),
    path('controles/ver/<int:control_id>/', views.ver_control, name='ver_control'),
    path('controles/editar/<int:control_id>/', views.editar_control, name='editar_control'),
    path('controles/historial/<int:control_id>/', views.historial_control, name='historial_control'),
    path('controles/configuracion/historial/', views.historial_configuracion, name='historial_configuracion'),
    path('controles/registrar_vacuna/<str:nino_rut>/', views.registrar_vacuna, name='registrar_vacuna'),
    path('vacunas/registrar/<int:vacuna_aplicada_id>/', views.registrar_vacuna, name='registrar_vacuna'),
    path('vacunas/editar/<int:vacuna_aplicada_id>/', views.editar_vacuna, name='editar_vacuna'),
    path('vacunas/ver/<int:vacuna_aplicada_id>/', views.ver_vacuna, name='ver_vacuna'),
    path('vacunas/historial/<int:vacuna_aplicada_id>/', views.historial_vacuna, name='historial_vacuna'),
    path('controles/configuracion/historial/', views.historial_configuracion, name='historial_configuracion'),
    path('vacunas/configuracion/', views.configurar_vacunas, name='configurar_vacunas'),
    path('vacunas/configuracion/historial/', views.historial_vacunas, name='historial_vacunas'),
    path('ninos/<str:nino_rut>/registrar-alergia/', views.registrar_alergia, name='registrar_alergia'),
    path('ninos/alergia/editar/<int:registro_alergia_id>/', views.editar_alergia, name='editar_alergia'),
    path('ninos/alergia/historial/<int:registro_alergia_id>/', views.historial_alergia, name='historial_alergia'),
    path('alergias/configuracion/', views.configurar_alergias, name='configurar_alergias'),
    path('alergias/tipo/historial/', views.historial_alergias, name='historial_alergias_tipo'),
    # --- RUTA GENERAL DESPUÉS --- si lo hacemos al reves la wea se muere a veces, creo que tiene que ver con que las rutas son similares
    path('ninos/', views.listar_ninos, name='listar_ninos'),
    path('controles/<str:nino_rut>/', views.controles, name='controles'),
]