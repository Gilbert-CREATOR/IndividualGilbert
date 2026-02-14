from django.urls import path
from carwashapp import views
from carwashapp.views import login_view, admin_stats
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # ==========================
    # RUTAS CLIENTE
    # ==========================
    path('', views.inicio, name='inicio'),
    path('agendar/', views.agendar_cita, name='agendar_cita'),
    path('registro/', views.registro, name='registro'),
    path('login/', login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/cambiar-contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('perfil/borrar/', views.borrar_usuario, name='borrar_usuario'),

    # ==========================
    # DASHBOARD EMPLEADO
    # ==========================
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/citas/', views.dashboard_citas, name='dashboard_citas'),
    path('dashboard/cita/<int:id>/', views.dashboard_cita_detalle, name='dashboard_cita_detalle'),
    path('dashboard/cita/<int:id>/eliminar/', views.eliminar_cita, name='eliminar_cita'),
    path('dashboard/cita/<int:id>/estado/<str:nuevo_estado>/', views.cambiar_estado_cita, name='cambiar_estado_cita'),
    path('dashboard/vehiculos/', views.empleado_vehiculos, name='empleado_vehiculos'),
    path('dashboard/empleado/', views.empleado_dashboard, name='empleado_dashboard'),

    # ==========================
    # API AUTOCOMPLETE
    # ==========================
    path('api/marcas/', views.api_marcas, name='api_marcas'),
    path('api/modelos/', views.api_modelos, name='api_modelos'),

    # ==========================
    # PANEL ADMINISTRADOR - SERVICIOS
    # ==========================
    path('panel/servicios/', views.servicio_list, name='servicio_list'),
    path('panel/servicios/nuevo/', views.servicio_create, name='servicio_create'),
    path('panel/servicios/<int:id>/editar/', views.servicio_edit, name='servicio_edit'),
    path('panel/servicios/<int:id>/toggle/', views.servicio_toggle, name='servicio_toggle'),

    # ==========================
    # PANEL ADMINISTRADOR - USUARIOS
    # ==========================
    path('administrador/usuario/nuevo/', views.admin_usuario_create, name='admin_usuario_create'),
    path('administrador/usuario/<int:id>/editar/', views.admin_usuario_edit, name='admin_usuario_edit'),
    path('administrador/usuario/<int:id>/eliminar/', views.admin_usuario_delete, name='admin_usuario_delete'),

    # ==========================
    # PANEL ADMINISTRADOR - EMPLEADOS
    # ==========================
    path('administrador/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('administrador/empleado/nuevo/', views.admin_empleado_create, name='admin_empleado_create'),
    path('administrador/empleado/<int:id>/eliminar/', views.admin_empleado_delete, name='admin_empleado_delete'),

    # ==========================
    # PANEL ADMINISTRADOR - ESTADÍSTICAS E HISTORIAL
    # ==========================
    path('administrador/stats/', admin_stats, name='admin_stats'),
    path('administrador/historial/', views.admin_historial, name='admin_historial'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)