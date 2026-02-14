from django.urls import reverse

def menu_principal(request):
    return {
        'menu': [
            {'name': 'Inicio', 'url': '/#inicio'},
            {'name': 'Servicios', 'url': '/#tarifa'},
            {'name': 'Agendar cita', 'url': reverse('agendar_cita')},
            {'name': 'Contacto', 'url': '/#Contacto'},
        ]
    }


def menu_empleado(request):
    return {
        'menu_empleado': [
            {'name': 'Inicio', 'url': reverse('inicio')},
            {'name': 'Perfil', 'url': reverse('perfil')},
            {'name': 'Agendar Cita', 'url': reverse('agendar_cita')},
            {'name': 'Dashboard', 'url': reverse('dashboard')},
            {'name': 'Cerrar Sesión', 'url': reverse('logout')},
        ]
    }


def menu_admin(request):
    return {
        'menu_admin': [
            {'name': 'Inicio', 'url': reverse('inicio')},
            {'name': 'Perfil', 'url': reverse('perfil')},
            {'name': 'Empleados', 'url': reverse('admin_dashboard')},
            {'name': 'Dashboard', 'url': reverse('dashboard')},  # si es el de empleado
            {'name': 'Servicios', 'url': reverse('servicio_list')},
            {'name': 'Estadísticas', 'url': reverse('admin_stats')},
            {'name': 'Historial', 'url': reverse('admin_historial')},
            {'name': 'Cerrar Sesión', 'url': reverse('logout')},
        ]
    }