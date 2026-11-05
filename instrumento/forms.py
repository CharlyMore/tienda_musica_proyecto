from decimal import Decimal

from django import forms

from .models import Instrumento


class InstrumentoForm(forms.ModelForm):
    stock = forms.IntegerField(
        min_value=1,
        max_value=100,
        error_messages={
            "min_value": "Las unidades en stock no pueden ser 0.",
            "max_value": "Las unidades en stock no pueden superar 100.",
        },
        widget=forms.NumberInput(attrs={"min": "1", "max": "100", "step": "1"}),
    )
    precio = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("100000"),
        max_value=Decimal("10000000"),
        widget=forms.NumberInput(
            attrs={"min": "100000", "max": "10000000", "step": "0.01"}
        ),
        help_text="",
    )

    class Meta:
        model = Instrumento
        fields = [
            "nombre",
            "marca",
            "categoria",
            "precio",
            "stock",
            "descripcion",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Ej. Guitarra acústica"}),
            "marca": forms.TextInput(attrs={"placeholder": "Ej. Yamaha"}),
            "descripcion": forms.Textarea(attrs={"rows": 4}),
        }
