# login/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from unidecode import unidecode

# Este Manager es necesario para decirle a Django cómo crear usuarios y superusuarios con nuestro modelo personalizado.
class UsuarioManager(BaseUserManager):
    def create_user(self, rut, email, nombre_completo, rol, password=None, **extra_fields):
        if not rut:
            raise ValueError('El usuario debe tener un RUT')
        if not rol:
            raise ValueError('El usuario debe tener un Rol asignado')
            
        email = self.normalize_email(email)
        user = self.model(rut=rut, email=email, nombre_completo=nombre_completo, rol=rol, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, rut, email, nombre_completo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        # Para el superusuario, buscamos el rol 'Administrador' o lo creamos si no existe.
        rol, created = Rol.objects.get_or_create(nombre_rol='Administrador', defaults={'descripcion':'Rol con acceso total al sistema.'})

        return self.create_user(rut, email, nombre_completo, rol, password, **extra_fields)


# Este modelo representa los roles que puede tener un usuario en el sistema.
class Rol(models.Model):
    id = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=30, unique=True)
    descripcion = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre_rol


# El modelo central para la autenticación. TODOS los que inician sesión son un 'Usuario'.
class Usuario(AbstractBaseUser, PermissionsMixin):
    rut = models.CharField(max_length=10, unique=True)
    nombre_completo = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT)
    clave_temporal = models.BooleanField(default=False) 

    # Campo normalizado
    nombre_completo_norm = models.CharField(
        max_length=200,
        editable=False,
        db_index=True
        # No necesita null=True porque nombre_completo es obligatorio
    )


    activo = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) # Necesario para el admin de Django
    fecha_creacion = models.DateTimeField(default=timezone.now)

    # Conectamos el manager
    objects = UsuarioManager()

    # Le decimos a Django que el campo para iniciar sesión es 'rut'
    USERNAME_FIELD = 'rut'
    # Campos requeridos al crear un usuario por consola
    REQUIRED_FIELDS = ['nombre_completo', 'email']

    # Función de normalización
    def _normalize_text(self, text):
        if text:
            return unidecode(text).lower()
        return text
    

    # Método save
    def save(self, *args, **kwargs):
        # Normaliza el nombre completo antes de guardar
        self.nombre_completo_norm = self._normalize_text(self.nombre_completo)
        super().save(*args, **kwargs) # Llama al save original
 

    def __str__(self):
        return f"{self.nombre_completo} ({self.rut})"


# Contiene la información específica de un Profesional. Está ligado 1 a 1 con un Usuario.
class Profesional(models.Model):
    ESPECIALIDAD_CHOICES = [
        ('Pediatra', 'Pediatra'),
        ('Enfermero/a', 'Enfermero/a'),
        ('Nutricionista', 'Nutricionista'),
        ('Medico General', 'Medico General'),
        ('Matron/a', 'Matron/a'),
    ]
    # Aquí está la magia: cada Profesional ES un Usuario.
    rut = models.CharField(max_length=10, primary_key=True) # El RUT es la clave
    nombre_completo = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    especialidad = models.CharField(max_length=30, choices=ESPECIALIDAD_CHOICES, default='Pediatra')
    encargado = models.BooleanField(default=False)
    
    # El usuario es opcional al principio
    usuario = models.OneToOneField(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='perfil_profesional')

    def __str__(self):
        return self.nombre_completo


# Contiene la información específica de un Tutor. También ligado 1 a 1 con un Usuario.
class Tutor(models.Model):
    
    # Cada Tutor ES un Usuario.
    rut = models.CharField(max_length=10, primary_key=True) # El RUT es la clave
    nombre_completo = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    
    # El usuario es opcional al principio
    usuario = models.OneToOneField(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='perfil_tutor')
    
    ninos = models.ManyToManyField('control.Nino', through='NinoTutor')

    def __str__(self):
        return self.nombre_completo


# La tabla intermedia que define la relación entre un Tutor y un Niño.
class NinoTutor(models.Model):

    PARENTESCO_CHOICES = [
        ('Madre', 'Madre'), 
        ('Padre', 'Padre'), 
        ('Abuela', 'Abuela'), 
        ('Abuelo', 'Abuelo'), 
        ('Tutor legal', 'Tutor legal'),
        ('Hermano/a', 'Hermano/a'),
        ('Tío', 'Tío'),
        ('Tía', 'Tía'),
    ]
    
    nino = models.ForeignKey('control.Nino', on_delete=models.CASCADE)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    fecha_ini = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    parentesco = models.CharField(max_length=35, choices=PARENTESCO_CHOICES, default='Madre')

    class Meta:
        unique_together = ('nino', 'tutor') # Para que no se pueda asignar el mismo tutor al mismo niño dos veces.
        verbose_name = "Relación Niño-Tutor"
        verbose_name_plural = "Relaciones Niño-Tutor"

    def __str__(self):
        return f"{self.tutor.nombre_completo} es tutor de {self.nino.nombre}"