import decimal

from django.core.validators import MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Instrumento",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=100, verbose_name="nombre")),
                ("marca", models.CharField(max_length=80, verbose_name="marca")),
                (
                    "categoria",
                    models.CharField(
                        choices=[
                            ("cuerda", "Cuerda"),
                            ("viento", "Viento"),
                            ("percusion", "Percusión"),
                            ("teclado", "Teclado"),
                            ("otro", "Otro"),
                        ],
                        max_length=20,
                        verbose_name="categoría",
                    ),
                ),
                (
                    "precio",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[MinValueValidator(decimal.Decimal("0.01"))],
                        verbose_name="precio",
                    ),
                ),
                ("stock", models.PositiveIntegerField(default=0, verbose_name="stock")),
                ("descripcion", models.TextField(blank=True, verbose_name="descripción")),
            ],
            options={
                "verbose_name": "instrumento",
                "verbose_name_plural": "instrumentos",
                "ordering": ["nombre", "marca"],
            },
        ),
    ]
