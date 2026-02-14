from django.contrib import admin
from .models import Marca, Modelo, Servicio, Cita, perfil
from django.utils.html import format_html


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    search_fields = ['nombre']


@admin.register(Modelo)
class ModeloAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'marca']
    list_filter = ['marca']
    search_fields = ['nombre']


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio']
    search_fields = ['nombre']


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'servicio', 'fecha', 'hora', 'estado']
    list_filter = ['estado', 'fecha']
    search_fields = ['nombre', 'telefono']

@admin.register(perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'mostrar_foto')

    def mostrar_foto(self, obj):
        if obj.foto_perfil:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius:50%;" />',
                obj.foto_perfil.url
            )
        return "Sin foto"

    mostrar_foto.short_description = 'Foto'
