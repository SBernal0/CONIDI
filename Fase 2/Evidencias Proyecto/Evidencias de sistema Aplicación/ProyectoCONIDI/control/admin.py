# control/admin.py

from django.contrib import admin
from .models import Region, Ciudad, Comuna, Nino, Control, PeriodoControl, Vacuna, VacunaAplicada, CategoriaAlergia, RegistroAlergias, EntregaAlimentos
from simple_history.admin import SimpleHistoryAdmin 

# Para una mejor visualización, registraremos cada modelo.
# Usamos decoradores para un registro más limpio.

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom_region')

@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    list_display = ('nom_ciudad', 'region')
    list_filter = ('region',)

@admin.register(Comuna)
class ComunaAdmin(admin.ModelAdmin):
    list_display = ('nom_comuna', 'ciudad')
    list_filter = ('ciudad__region',)

@admin.register(Nino)
class NinoAdmin(admin.ModelAdmin):
    list_display = ('rut_nino', 'nombre', 'ap_paterno', 'fecha_nacimiento', 'comuna')
    search_fields = ('rut_nino', 'nombre', 'ap_paterno')

@admin.register(Control)
class ControlAdmin(SimpleHistoryAdmin):
    list_display = ('nino', 'nombre_control', 'fecha_control_programada', 'profesional', 'estado_control')
    list_filter = ('estado_control', 'profesional')
    search_fields = ('nino__nombre', 'nino__rut_nino')

# Registramos los demás modelos de forma simple
class PeriodoControlAdmin(admin.ModelAdmin):
    # Mostramos todos los campos importantes en la lista
    list_display = ('nombre_mes_control', 'mes_control', 'dias_margen')
    # Hacemos que los días de margen sean editables directamente en la lista
    list_editable = ('mes_control', 'dias_margen')
    ordering = ('mes_control',)



admin.site.register(Vacuna)
admin.site.register(CategoriaAlergia)
admin.site.register(RegistroAlergias)

admin.site.register(VacunaAplicada)
admin.site.register(EntregaAlimentos)