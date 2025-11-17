# control/urls.py
from django.urls import path
from . import views

app_name = 'control' # Espacio de nombres para evitar colisiones

urlpatterns = [
    # --- Vistas Principales (Relacionadas con el Niño) ---
    path('ninos/', views.listar_ninos, name='listar_ninos'),
    # Vista general del niño con pestañas
    path('ninos/<str:nino_rut>/', views.controles, name='detalle_nino'), 

    # --- Gestión de Controles de Niño Sano ---
    path('controles/registrar/<int:control_id>/', views.registrar_control, name='registrar_control'),
    path('controles/ver/<int:control_id>/', views.ver_control, name='ver_control'),
    path('controles/editar/<int:control_id>/', views.editar_control, name='editar_control'),
    path('controles/historial/<int:control_id>/', views.historial_control, name='historial_control'),

    # --- Gestión de Vacunas Aplicadas ---
    # Usamos el ID del registro VacunaAplicada
    path('vacunas/registrar/<int:vacuna_aplicada_id>/', views.registrar_vacuna, name='registrar_vacuna'), 
    path('vacunas/ver/<int:vacuna_aplicada_id>/', views.ver_vacuna, name='ver_vacuna'),
    path('vacunas/editar/<int:vacuna_aplicada_id>/', views.editar_vacuna, name='editar_vacuna'),
    path('vacunas/historial/<int:vacuna_aplicada_id>/', views.historial_vacuna, name='historial_vacuna'),

    # --- Gestión de Alergias Registradas ---
    # Usamos el RUT del niño para iniciar el registro
    path('ninos/<str:nino_rut>/registrar-alergia/', views.registrar_alergia, name='registrar_alergia'), 
    # Usamos el ID del registro RegistroAlergias para editar/ver historial
    path('ninos/alergia/editar/<int:registro_alergia_id>/', views.editar_alergia, name='editar_alergia'),
    path('ninos/alergia/historial/<int:registro_alergia_id>/', views.historial_alergia, name='historial_alergia'),

    # --- Páginas de Configuración (Solo Admin) ---
    # Periodos de Control
    path('configuracion/periodos/', views.configurar_periodos, name='configurar_periodos'),
    path('configuracion/periodos/historial/', views.historial_configuracion, name='historial_configuracion'),
    # Vacunas
    path('configuracion/vacunas/', views.configurar_vacunas, name='configurar_vacunas'),
    path('configuracion/vacunas/historial/', views.historial_vacunas, name='historial_vacunas'),
    # Categorías de Alergia
    path('configuracion/alergias/categorias/', views.configurar_categorias_alergia, name='configurar_categorias_alergia'),
    path('configuracion/alergias/categorias/historial/', views.historial_categorias_alergia, name='historial_categorias_alergia'),
    # Reportes por correo
    path('configuracion/reportes/', views.reportes, name='reportes'),
    path('configuracion/reportes/historial/', views.historial_envio_reportes, name='historial_envio_reportes'),

# --- RUTA NUEVA PARA EL DASHBOARD BI ---
    path('dashboard/bi/', views.dashboard_bi, name='dashboard_bi'),
]