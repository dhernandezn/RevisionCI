from django.db import models

# Create your models here.
class Autoexcluidos(models.Model):
    # Datos del cliente
    run = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    mobile_phone = models.CharField(max_length=50, null=True, blank=True)

    # Datos del apoderado
    apo_name = models.CharField(max_length=255, null=True, blank=True)
    apo_first_name = models.CharField(max_length=255, null=True, blank=True)
    apo_last_name = models.CharField(max_length=255, null=True, blank=True)
    apo_email = models.EmailField(null=True, blank=True)
    apo_phone = models.CharField(max_length=50, null=True, blank=True)
    apo_mobile_phone = models.CharField(max_length=50, null=True, blank=True)

    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.run} - {self.first_name} {self.last_name}"
    
class Prohibidos(models.Model):
    #Datos tabla prohibidos
    rut = models.CharField(max_length=255, unique=True)
    nombre = models.CharField(max_length=255, null=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.rut} - {self.nombre} {self.fecha_inicio} / {self.fecha_fin}"