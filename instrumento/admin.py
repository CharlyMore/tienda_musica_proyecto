from django.contrib import admin

from .models import Instrumento


class InstrumentoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "marca", "categoria", "precio", "stock")
    list_filter = ("categoria", "marca")
    search_fields = ("nombre", "marca", "descripcion")


admin.site.register(Instrumento, InstrumentoAdmin)
