from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

# --- GESTOR DE USUARIOS PERSONALIZADO ---
class UsuarioManager(BaseUserManager):
    def create_user(self, rut, email=None, password=None, **extra_fields):
        if not rut:
            raise ValueError('El usuario debe tener un RUT')
        email = self.normalize_email(email)
        user = self.model(rut=rut, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, rut, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(rut, email, password, **extra_fields)


# --- TABLA DE ROLES ---
class TipoUsuario(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


# --- USUARIO PERSONALIZADO ---
class Usuario(AbstractBaseUser, PermissionsMixin):
    rut = models.CharField(max_length=12, unique=True)
    nombre_completo = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    tipo_usuario = models.ForeignKey(TipoUsuario, on_delete=models.PROTECT)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    activo = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    clave_temporal = models.BooleanField(default=False)  # NUEVO CAMPO

    objects = UsuarioManager()

    USERNAME_FIELD = 'rut'
    REQUIRED_FIELDS = ['nombre_completo', 'tipo_usuario', 'email']

    def __str__(self):
        return f"{self.nombre_completo} ({self.rut})"
