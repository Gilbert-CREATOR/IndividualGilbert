from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# ==========================
# MODELO MARCA
# ==========================
class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# ==========================
# MODELO MODELO
# ==========================
class Modelo(models.Model):
    marca = models.ForeignKey(
        Marca,
        on_delete=models.CASCADE,
        related_name='modelos'
    )
    nombre = models.CharField(max_length=100)

    class Meta:
        ordering = ['nombre']
        unique_together = ('marca', 'nombre')

    def __str__(self):
        return f"{self.marca.nombre} {self.nombre}"


# ==========================
# MODELO CITA
# ==========================
class Cita(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(max_length=254, blank=True, null=True)

    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True)
    modelo = models.ForeignKey(Modelo, on_delete=models.SET_NULL, null=True, blank=True)

    servicio = models.ForeignKey('Servicio', on_delete=models.CASCADE)  # ✅ ForeignKey
    fecha = models.DateField()
    hora = models.CharField(max_length=5)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('confirmada', 'Confirmada'),
            ('en_proceso', 'En Proceso'),
            ('cancelada', 'Cancelada'),
            ('finalizada', 'Finalizada'),
        ],
        default='pendiente'
    )
    correo_enviado = models.BooleanField(default=False)
    creada = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.marca and self.modelo:
            return f"{self.nombre} - {self.marca} {self.modelo.nombre}"
        return f"{self.nombre} - {self.fecha} {self.hora}"

    # Métodos para usar en templates
    def puede_finalizar(self):
        return self.estado in ['confirmada', 'en_proceso']

    def puede_cancelar(self):
        return self.estado != 'finalizada'

    def puede_confirmar(self):
        return self.estado == 'pendiente'

    def puede_en_proceso(self):
        return self.estado == 'confirmada'


# ==========================
# MODELO VEHICULO
# ==========================
class Vehiculo(models.Model):
    marca = models.ForeignKey(
        Marca,
        on_delete=models.PROTECT
    )
    modelo = models.ForeignKey(
        Modelo,
        on_delete=models.PROTECT
    )

    def __str__(self):
        return f"{self.marca.nombre} {self.modelo.nombre}"

# ==========================
# Perfil de empleado
# ==========================

class perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_contratacion = models.DateField(default=timezone.now)
    foto_perfil = models.ImageField(upload_to='perfil/', blank=True, null=True)

    def __str__(self):
        return self.nombre
    
# ==========================
# Señal para crear/actualizar servicios
# ==========================

class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.nombre
