from django import forms
from .models import Cita, Marca, Modelo
from .models import perfil, Servicio
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm

HORAS_BASE = [
    '07:00','07:30','08:00','08:30','09:00','09:30',
    '10:00','10:30','11:00','11:30','12:00','12:30',
    '13:00','13:30','14:00','14:30',
    '15:00','15:30','16:00','16:30',
    '17:00','17:30','18:00','18:30',
    '19:00','19:30','20:00'
]


class CitaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        fecha = kwargs.pop('fecha', None)
        super().__init__(*args, **kwargs)

        # --- Filtrar horas disponibles ---
        horas_disponibles = HORAS_BASE
        if fecha:
            horas_ocupadas = Cita.objects.filter(fecha=fecha).values_list('hora', flat=True)
            horas_disponibles = [h for h in HORAS_BASE if h not in horas_ocupadas]

        self.fields['hora'] = forms.ChoiceField(
            choices=[(h, h) for h in horas_disponibles]
        )

        # --- Inicializar queryset de modelos vacío ---
        self.fields['modelo'].queryset = Modelo.objects.none()

        # --- Si hay marca seleccionada, filtrar modelos ---
        if 'marca' in self.data:
            try:
                marca_id = int(self.data.get('marca'))
                self.fields['modelo'].queryset = Modelo.objects.filter(marca_id=marca_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.marca:
            self.fields['modelo'].queryset = Modelo.objects.filter(marca=self.instance.marca)

    class Meta:
        model = Cita
        fields = ['nombre', 'telefono', 'email', 'marca', 'modelo', 'servicio', 'fecha', 'hora']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'})
        }


class PerfilForm(forms.ModelForm):
    class Meta:
        model = perfil
        fields = ['foto_perfil']

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'descripcion', 'precio']

# ==========================
# Crear usuario X admin
# ==========================

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']