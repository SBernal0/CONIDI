from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, TipoUsuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ('rut', 'nombre_completo', 'tipo_usuario', 'email', 'activo', 'is_staff')
    list_filter = ('tipo_usuario', 'activo', 'is_staff')
    fieldsets = (
        (None, {'fields': ('rut', 'password')}),
        ('Información personal', {'fields': ('nombre_completo', 'email', 'tipo_usuario')}),
        ('Permisos', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas', {'fields': ('last_login', 'fecha_creacion')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('rut', 'nombre_completo', 'email', 'tipo_usuario', 'password1', 'password2', 'is_staff', 'is_superuser', 'activo'),
        }),
    )
    search_fields = ('rut', 'nombre_completo', 'email')
    ordering = ('rut',)

@admin.register(TipoUsuario)
class TipoUsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')