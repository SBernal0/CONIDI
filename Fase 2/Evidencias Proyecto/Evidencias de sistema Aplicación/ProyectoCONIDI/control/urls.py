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

    # --- RUTA GENERAL DESPUÉS --- si lo hacemos al reves la wea se muere a veces, creo que tiene que ver con que las rutas son similares
    path('ninos/', views.listar_ninos, name='listar_ninos'),
    path('controles/<str:nino_rut>/', views.controles, name='controles'),
]