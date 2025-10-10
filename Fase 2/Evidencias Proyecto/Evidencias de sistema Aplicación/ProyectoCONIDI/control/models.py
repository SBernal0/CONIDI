from django.db import models

# Create your models here.
class Nino(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    rut = models.CharField(max_length=12, unique=True)

    def __str__(self):
        return self.nombre