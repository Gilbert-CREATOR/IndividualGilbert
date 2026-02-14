from django.shortcuts import render, redirect, get_object_or_404
from .forms import CitaForm, PerfilForm, ServicioForm, EmpleadoForm
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Vehiculo, Cita, Marca, Modelo, Servicio
from django.contrib.auth import authenticate, login as auth_login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.conf import settings
import threading
import logging
from django.contrib.admin.views.decorators import staff_member_required
from functools import wraps
from django.http import JsonResponse
from django.db.models import Count, Sum
from django.db.models.functions import ExtractMonth, TruncDate
from django.utils.timezone import now
from .models import Cita, Servicio
from .models import perfil
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
import json
from django.core.paginator import Paginator
from django.db.models import Q


logger = logging.getLogger(__name__)


# ===================================
#       VISTAS DEL CLIENTE
# ===================================

def inicio(request):
    """Página de inicio con listado de servicios."""
    servicios = Servicio.objects.all()
    return render(request, 'pages/cliente/inicio.html', {'servicios': servicios})


def zonadeservicio(request):
    """Página de zona de servicios (informativa)."""
    return render(request, 'pages/cliente/servicios.html')


def sobrenosotros(request):
    """Página sobre nosotros (informativa)."""
    return render(request, 'pages/cliente/servicios.html')


def agendar_cita(request):
    servicios = Servicio.objects.all()
    fecha = None

    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        form = CitaForm(request.POST, fecha=fecha)

        marca_id = request.POST.get('marca')
        modelo_id = request.POST.get('modelo')
        servicio_id = request.POST.get('servicio')

        # Validaciones
        if not marca_id:
            form.add_error(None, "Debes seleccionar una marca válida.")
        if not modelo_id:
            form.add_error(None, "Debes seleccionar un modelo válido.")
        if not servicio_id:
            form.add_error(None, "Debes seleccionar un servicio.")

        if form.is_valid():
            cita = form.save(commit=False)
            cita.marca = Marca.objects.get(id=marca_id)
            cita.modelo = Modelo.objects.get(id=modelo_id)
            cita.servicio = Servicio.objects.get(id=servicio_id)
            cita.save()
            messages.success(request, "Tu cita ha sido agendada correctamente.")
            return redirect('inicio')
        else:
            print(form.errors) 

    else:
        form = CitaForm(fecha=fecha)

    return render(request, 'pages/cliente/agendar.html', {
        'form': form,
        'servicios': servicios
    })

# ===================================
#       FUNCIONES DE CORREO
# ===================================

def enviar_correo_cita(cita):
    """
    Envia correo al cliente según el estado de la cita.
    Retorna True si se envió correctamente.
    """
    if not cita.email:
        return False

    fecha_formateada = cita.fecha.strftime('%d/%m/%Y') if hasattr(cita.fecha, 'strftime') else cita.fecha
    hora_formateada = cita.hora

    if cita.estado == "confirmada":
        asunto = "Cita confirmada - CarWash"
        mensaje = f"Hola {cita.nombre}, tu cita con el servicio {cita.servicio} ha sido CONFIRMADA el {fecha_formateada} a las {hora_formateada}."
        html_mensaje = f"""<div style="font-family: Arial; color: #333;">
            <h2 style="color: #2E86C1;">¡Hola {cita.nombre}!</h2>
            <p>Tu cita ha sido <b style="color:green;">CONFIRMADA</b> ✅</p>
            <p><b>Servicio:</b> {cita.servicio}<br><b>Fecha:</b> {fecha_formateada}<br><b>Hora:</b> {hora_formateada}<br><b>Vehículo:</b> {cita.modelo}</p>
        </div>"""

    elif cita.estado == "en_proceso":
        asunto = "Tu vehículo está en proceso - CarWash"
        mensaje = f"Hola {cita.nombre}, tu vehículo está EN PROCESO."
        html_mensaje = f"""<div><p>Tu vehículo {cita.modelo} está EN PROCESO 🔧</p></div>"""

    elif cita.estado == "finalizada":
        asunto = "Servicio finalizado - CarWash"
        mensaje = f"Hola {cita.nombre}, tu servicio ha sido FINALIZADO."
        html_mensaje = f"""<div><p>Tu servicio {cita.modelo} ha sido FINALIZADO ✅</p></div>"""

    elif cita.estado == "cancelada":
        asunto = "Cita cancelada - CarWash"
        mensaje = f"Hola {cita.nombre}, tu cita ha sido CANCELADA."
        html_mensaje = f"""<div><p>Tu cita para el vehiculo {cita.modelo} ha sido CANCELADA ❌</p></div>"""
    else:
        return False

    try:
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [cita.email],
            fail_silently=False,
            html_message=html_mensaje
        )
        return True
    except Exception as e:
        logger.error(f"Error enviando correo a {cita.email}: {e}")
        return False


def cambiar_estado_cita(request, id, nuevo_estado):
    """
    Cambia el estado de una cita y envía correo al cliente en segundo plano.
    """
    cita = Cita.objects.get(id=id)
    cita.estado = nuevo_estado
    cita.save()

    if cita.email:
        def enviar():
            try:
                enviado = enviar_correo_cita(cita)
                cita.correo_enviado = enviado
                cita.save()
            except Exception as e:
                logger.error(f"Error en hilo de correo: {e}")

        threading.Thread(target=enviar).start()
        messages.success(request, "Estado actualizado. Correo enviado en segundo plano.")
    else:
        messages.warning(request, "El cliente no tiene email registrado.")

    return redirect('empleado_dashboard')


# ===================================
#       VISTAS DEL EMPLEADO
# ===================================

def login(request):
    return render(request, 'pages/empleado/login_empleado.html')


@staff_member_required
def dashboard(request):
    """Dashboard principal para empleados."""
    citas = Cita.objects.all().order_by('-fecha', '-hora')
    return render(request, 'pages/empleado/index.html', {'citas': citas})


@staff_member_required
def empleado_dashboard(request):
    """Dashboard alternativo de empleado (mismo que dashboard)."""
    citas = Cita.objects.all()
    return render(request, 'pages/empleado/index.html', {'citas': citas})


@login_required
def perfil(request):
    user = request.user
    from .models import perfil

    perfil_obj, created = perfil.objects.get_or_create(
        user=user,
        defaults={
            'nombre': user.get_full_name() or user.username,
            'email': user.email
        }
    )

    form_password = PasswordChangeForm(user, request.POST or None)
    form_foto = PerfilForm(
        request.POST or None,
        request.FILES or None,
        instance=perfil_obj
    )

    if request.method == 'POST':
        if 'cambiar_contrasena' in request.POST:
            if form_password.is_valid():
                user = form_password.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Contraseña cambiada correctamente.')
                return redirect('perfil')
            messages.error(request, 'Corrige los errores del formulario.')

        elif 'borrar_usuario' in request.POST:
            user.delete()
            logout(request)
            return redirect('inicio')

        elif 'foto_perfil' in request.FILES:
            if form_foto.is_valid():
                form_foto.save()
                messages.success(request, 'Foto de perfil actualizada.')
                return redirect('perfil')
            messages.error(request, 'Error al subir la foto.')

    return render(request, 'pages/empleado/perfil.html', {
        'user': user,
        'perfil': perfil_obj,
        'form': form_password,
        'form_foto': form_foto
    })


@login_required
def cambiar_contrasena(request):
    """Cambiar contraseña del empleado."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Contraseña cambiada correctamente.')
            return redirect('perfil')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'pages/empleado/cambiar_contrasena.html', {'form': form})


@login_required
def borrar_usuario(request):
    """Eliminar usuario actual."""
    if request.method == 'POST':
        request.user.delete()
        logout(request)
        return redirect('inicio')
    return render(request, 'pages/empleado/borrar_usuario.html')


@login_required
def eliminar_cita(request, id):
    """Eliminar una cita por ID."""
    cita = get_object_or_404(Cita, id=id)
    if request.method == 'POST':
        cita.delete()
        messages.success(request, "Cita eliminada correctamente")
    return redirect('empleado_dashboard')


@login_required
def dashboard_citas(request):
    """Vista de todas las citas para dashboard."""
    citas = Cita.objects.order_by('fecha', 'hora')
    return render(request, 'dashboard/citas.html', {'citas': citas})


@login_required
def dashboard_cita_detalle(request, id):
    """Detalle de una cita específica."""
    cita = Cita.objects.get(id=id)
    return render(request, 'dashboard/detalle.html', {'cita': cita})


@login_required
def empleado_vehiculos(request):
    """Lista de vehículos en el dashboard."""
    vehiculos = Vehiculo.objects.order_by('-hora')
    return render(request, 'dashboard/vehiculos.html', {'vehiculos': vehiculos})


# ===================================
#       AUTENTICACIÓN
# ===================================

def login_view(request):
    """Login de empleados."""
    if request.user.is_authenticated:
        return redirect('empleado_dashboard')

    if request.method == 'POST':
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            messages.error(request, "Por favor, complete todos los campos.")
            return render(request, 'pages/empleado/login_empleado.html')

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Credenciales inválidas. Inténtelo de nuevo.")
            return render(request, 'pages/empleado/login_empleado.html')

        auth_login(request, user)
        messages.success(request, f"Bienvenido {user.first_name or user.username}!")
        return redirect('empleado_dashboard')

    return render(request, 'pages/empleado/login_empleado.html')


def registro(request):
    """Registro de un nuevo empleado."""
    if request.user.is_authenticated:
        return redirect('empleado_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password1 = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()

        if not username or not password1 or not password2:
            messages.error(request, 'Complete todos los campos obligatorios.')
            return render(request, 'pages/empleado/registro_empleado.html')

        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'pages/empleado/registro_empleado.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Este usuario ya existe.')
            return render(request, 'pages/empleado/registro_empleado.html')

        user = User.objects.create_user(username=username, email=email, password=password1)
        auth_login(request, user)
        messages.success(request, f'Bienvenido {user.username}')
        return redirect('empleado_dashboard')

    return render(request, 'pages/empleado/registro_empleado.html')


def logout_view(request):
    """Cerrar sesión del empleado."""
    logout(request)
    return redirect('inicio')


# ===================================
#       AUTOCOMPLETE MARCAS / MODELOS
# ===================================

def buscar_marcas(request):
    """Buscar marcas para autocomplete."""
    q = request.GET.get('q', '')
    marcas = Marca.objects.filter(nombre__icontains=q).order_by('nombre')[:10]
    data = [{'id': marca.id, 'nombre': marca.nombre} for marca in marcas]
    return JsonResponse(data, safe=False)


def buscar_modelos(request):
    """Buscar modelos según la marca para autocomplete."""
    q = request.GET.get('q', '')
    marca_id = request.GET.get('marca_id')
    if not marca_id:
        return JsonResponse([], safe=False)
    modelos = Modelo.objects.filter(marca_id=marca_id, nombre__icontains=q).order_by('nombre')[:10]
    data = [{'id': modelo.id, 'nombre': modelo.nombre} for modelo in modelos]
    return JsonResponse(data, safe=False)


def api_marcas(request):
    """API de marcas (similar a buscar_marcas)."""
    q = request.GET.get('q', '')
    marcas = Marca.objects.filter(nombre__icontains=q).order_by('nombre')[:10]
    data = [{"id": marca.id, "nombre": marca.nombre} for marca in marcas]
    return JsonResponse(data, safe=False)


def api_modelos(request):
    """API de modelos según la marca (similar a buscar_modelos)."""
    q = request.GET.get('q', '')
    marca_id = request.GET.get('marca_id')
    if not marca_id:
        return JsonResponse([], safe=False)
    modelos = Modelo.objects.filter(marca_id=marca_id, nombre__icontains=q).order_by('nombre')[:10]
    data = [{"id": modelo.id, "nombre": modelo.nombre} for modelo in modelos]
    return JsonResponse(data, safe=False)


# ===================================
#       VISTAS DE SERVICIOS
# ===================================
@login_required
def servicio_list(request):
    servicios = Servicio.objects.all().order_by('nombre')
    return render(request, 'panel/servicios/list.html', {'servicios': servicios})

@login_required
def servicio_create(request):
    form = ServicioForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('servicio_list')
    return render(request, 'panel/servicios/form.html', {'form': form, 'titulo': 'Nuevo Servicio'})

@login_required
def servicio_edit(request, id):
    servicio = get_object_or_404(Servicio, id=id)
    form = ServicioForm(request.POST or None, instance=servicio)
    if form.is_valid():
        form.save()
        return redirect('servicio_list')
    return render(request, 'panel/servicios/form.html', {'form': form, 'titulo': 'Editar Servicio'})

@login_required
def servicio_toggle(request, id):
    servicio = get_object_or_404(Servicio, id=id)
    servicio.activo = not servicio.activo
    servicio.save()
    return redirect('servicio_list')

# ===================================
#       VISTAS DE USUARIOS
# ===================================

def admin_usuario_create(request):
    form = ServicioForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('servicio_list')
    return render(request, 'panel/usuarios/form.html', {'form': form, 'titulo': 'Nuevo Usuario'})

@login_required
def admin_usuario_edit(request, id):
    servicio = get_object_or_404(Servicio, id=id)
    form = ServicioForm(request.POST or None, instance=servicio)
    if form.is_valid():
        form.save()
        return redirect('servicio_list')
    return render(request, 'panel/usuarios/form.html', {'form': form, 'titulo': 'Editar Usuario'})

@login_required
def admin_usuario_delete(request, id):
    servicio = get_object_or_404(Servicio, id=id)
    servicio.delete()
    return redirect('servicio_list')

# ===================================
#       DECORADOR DE ADMIN
# ===================================
def admin_required(view_func):
    """Decorator para restringir vista solo a administradores."""
    return user_passes_test(lambda u: u.is_staff, login_url='login')(view_func)

# ===================================
#       DECORADOR DE ADMIN
# ===================================
def admin_required(view_func):
    """Decorator para restringir vista solo a administradores."""
    return user_passes_test(lambda u: u.is_staff, login_url='login')(view_func)

# ===================================
#       DASHBOARD ADMINISTRADOR
# ===================================
@admin_required
def admin_dashboard(request):
    empleados = User.objects.filter(is_staff=True)
    return render(request, 'pages/administrador/dashboard.html', {
        'empleados': empleados
    })

# ===================================
#       CREAR EMPLEADO
# ===================================
@admin_required
def admin_empleado_create(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True

            # 🔐 CONTRASEÑA TEMPORAL EN TEXTO PLANO
            password = get_random_string(10)

            # ⛔ IMPORTANTE: set_password, NO user.password =
            user.set_password(password)
            user.save()

            # 📧 CORREO
            if user.email:
                send_mail(
                    subject='Acceso al sistema',
                    message=(
                        f'Hola {user.username},\n\n'
                        'Has sido agregado como empleado.\n\n'
                        f'Usuario: {user.username}\n'
                        f'Contraseña: {password}\n\n'
                        'Por favor cambia tu contraseña al iniciar sesión.\n\n'
                        'Saludos.'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )

            messages.success(
                request,
                f'Empleado {user.username} creado y correo enviado.'
            )
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        form = EmpleadoForm()

    return render(
        request,
        'panel/usuarios/form.html',
        {'form': form, 'titulo': 'Nuevo Empleado'}
    )

# ===================================
#       ELIMINAR EMPLEADO
# ===================================
@admin_required
def admin_empleado_delete(request, id):
    empleado = get_object_or_404(User, id=id, is_staff=True)
    empleado.delete()
    messages.success(request, f'Empleado {empleado.username} eliminado correctamente.')
    return redirect('admin_dashboard')

# ===================================
#       ESTADÍSTICAS ADMINISTRADOR
# ===================================

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff, login_url='login')(view_func)

@admin_required
def admin_stats(request):

    # ===============================
    # Citas por Estado
    # ===============================
    citas_estado_qs = (
        Cita.objects.values('estado')
        .annotate(total=Count('id'))
        .order_by('estado')
    )

    estados = [c['estado'] for c in citas_estado_qs]
    totales_estado = [c['total'] for c in citas_estado_qs]


    # ===============================
    # Ingresos por Mes (solo finalizadas)
    # ===============================
    ingresos_mes_qs = (
        Cita.objects.filter(estado='finalizada')
        .annotate(mes=ExtractMonth('fecha'))
        .values('mes')
        .annotate(total=Sum('servicio__precio'))
        .order_by('mes')
    )

    meses = [c['mes'] for c in ingresos_mes_qs]
    totales_ingresos = [float(c['total']) if c['total'] else 0 for c in ingresos_mes_qs]


    # ===============================
    # Servicios más Populares
    # ===============================
    servicios_qs = (
        Cita.objects.values('servicio__nombre')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )

    nombres_servicios = [c['servicio__nombre'] for c in servicios_qs]
    totales_servicios = [c['total'] for c in servicios_qs]


    # ===============================
    # Citas por Día
    # ===============================
    citas_dia_qs = (
        Cita.objects
        .annotate(dia=TruncDate('fecha'))
        .values('dia')
        .annotate(total=Count('id'))
        .order_by('dia')
    )

    dias = [c['dia'].strftime('%d-%m-%Y') for c in citas_dia_qs]
    totales_dia = [c['total'] for c in citas_dia_qs]


    context = {
        'estados': json.dumps(estados),
        'totales_estado': json.dumps(totales_estado),

        'meses': json.dumps(meses),
        'totales_ingresos': json.dumps(totales_ingresos),

        'nombres_servicios': json.dumps(nombres_servicios),
        'totales_servicios': json.dumps(totales_servicios),

        'dias': json.dumps(dias),
        'totales_dia': json.dumps(totales_dia),
    }

    return render(request, 'pages/administrador/stats.html', context)

# ===================================
#       ROLES DEL NAVBAR
# ===================================

def user_role(request):
    role = "cliente"  # valor por defecto
    if request.user.is_authenticated:
        if request.user.is_superuser:
            role = "admin"
        elif request.user.is_staff:
            role = "empleado"
    return {'user_role': role}

# ===================================
#       HISTORIAL DE CITAS (ADMIN)
# ===================================


def admin_historial(request):
    """
    Vista para mostrar todas las citas del negocio desde el inicio hasta hoy,
    con filtros opcionales y paginación.
    """
    # Query inicial: todas las citas
    citas = Cita.objects.select_related('servicio', 'marca', 'modelo').all().order_by('-fecha')

    # ==================== FILTROS ====================
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    estado = request.GET.get('estado')
    servicio_id = request.GET.get('servicio')

    if fecha_inicio:
        citas = citas.filter(fecha__gte=fecha_inicio)

    if fecha_fin:
        citas = citas.filter(fecha__lte=fecha_fin)
    if estado:
        citas = citas.filter(estado=estado)
    if servicio_id:
        citas = citas.filter(servicio_id=servicio_id)

    # ==================== PAGINACIÓN ====================
    paginator = Paginator(citas, 20)  # 20 citas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'servicios': Servicio.objects.all(),
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'estado': estado,
        'servicio_id': servicio_id,
    }

    return render(request, 'pages/administrador/historial.html', context)