# carwashapp/context_processors.py

def user_role(request):
    """
    Devuelve el rol del usuario para templates:
    - 'admin' si es superusuario
    - 'empleado' si es staff
    - 'cliente' por defecto
    """
    role = "cliente"  # valor por defecto
    if request.user.is_authenticated:
        if request.user.is_superuser:
            role = "admin"
        elif request.user.is_staff:
            role = "empleado"
    return {'user_role': role}