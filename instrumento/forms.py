from django import forms

from .models import Instrumento


class InstrumentoForm(forms.ModelForm):
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
            "precio": forms.NumberInput(attrs={"min": "0.01", "step": "0.01"}),
            "stock": forms.NumberInput(attrs={"min": "0", "step": "1"}),
            "descripcion": forms.Textarea(attrs={"rows": 4}),
        }
