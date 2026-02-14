from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import perfil
from django.apps import AppConfig

class CarwashappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'carwashapp'