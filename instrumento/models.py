from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Instrumento(models.Model):
    class Categoria(models.TextChoices):
        CUERDA = "cuerda", "Cuerda"
        VIENTO = "viento", "Viento"
        PERCUSION = "percusion", "Percusión"
        TECLADO = "teclado", "Teclado"
        OTRO = "otro", "Otro"

    nombre = models.CharField("nombre", max_length=100)
    marca = models.CharField("marca", max_length=80)
    categoria = models.CharField(
        "categoría",
        max_length=20,
        choices=Categoria.choices,
    )
    precio = models.DecimalField(
        "precio",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    stock = models.PositiveIntegerField("stock", default=0)
    descripcion = models.TextField("descripción", blank=True)

    class Meta:
        ordering = ["nombre", "marca"]
        verbose_name = "instrumento"
        verbose_name_plural = "instrumentos"

    def __str__(self):
        return f"{self.nombre} - {self.marca}"
