# login/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, Rol, Profesional, Tutor, NinoTutor

class ProfesionalInline(admin.StackedInline):
    model = Profesional
    can_delete = False
    verbose_name_plural = 'Perfil Profesional'

class TutorInline(admin.StackedInline):
    model = Tutor
    can_delete = False
    verbose_name_plural = 'Perfil de Tutor'

@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ('rut', 'nombre_completo', 'rol', 'email', 'activo', 'is_staff')
    list_filter = ('rol', 'is_staff', 'activo')
    
    fieldsets = (
        (None, {'fields': ('rut', 'password')}),
        ('Información Personal', {'fields': ('nombre_completo', 'email', 'rol')}),
        ('Permisos', {'fields': ('activo', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'fecha_creacion')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('rol',)}),
    )
    search_fields = ('rut', 'nombre_completo', 'email')
    ordering = ('rut',)
    
    inlines = []

    def get_inlines(self, request, obj=None):
        if obj and obj.rol:
            if obj.rol.nombre_rol == 'Profesional':
                return [ProfesionalInline]
            if obj.rol.nombre_rol == 'Tutor':
                return [TutorInline]
        return []

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre_rol', 'descripcion')

# --- AÑADIDO PARA SOLUCIONAR EL ERROR ---
@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre_completo', 'email', 'usuario')
    # Esto le dice al autocompletador qué campos puede usar para buscar un tutor
    search_fields = ('rut', 'nombre_completo', 'email') 
# ----------------------------------------

@admin.register(NinoTutor)
class NinoTutorAdmin(admin.ModelAdmin):
    list_display = ('nino', 'tutor', 'fecha_ini', 'fecha_fin','parentesco')
    autocomplete_fields = ['nino', 'tutor']