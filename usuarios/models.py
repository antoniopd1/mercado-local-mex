# usuarios/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging # Importar el módulo de logging

# Importa tu función de utilidad para actualizar los claims de Firebase
from .utils import update_firebase_custom_claim

# Crear una instancia de logger para este módulo
logger = logging.getLogger(__name__)

class CustomUser(AbstractUser):
    uid = models.CharField(max_length=128, unique=True, null=True, blank=True)
    is_business_owner = models.BooleanField(default=False)
    stripe_customer_id = models.CharField(max_length=50, null=True, blank=True)
    
    # Nuevo campo para el estado de la suscripción, si lo estás utilizando
    has_active_subscription = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Almacena el valor original de 'is_business_owner' cuando la instancia se carga de la DB
        self.__original_is_business_owner = self.is_business_owner

    def __str__(self):
        return self.email if self.email else self.username

# --- Signal para actualizar los custom claims de Firebase ---
@receiver(post_save, sender=CustomUser)
def sync_is_business_owner_with_firebase(sender, instance, created, **kwargs):
    """
    Sincroniza el campo is_business_owner del usuario de Django con los custom claims
    de Firebase cada vez que un CustomUser es guardado o creado.
    """
    if kwargs.get('raw', False):
        return

    # Usar logging en lugar de print
    logger.info(f"Signal activado para {instance.email}. Creado: {created}. is_business_owner actual (post-save): {instance.is_business_owner}")

    if instance.uid:
        # Obtener el valor original del campo (antes de la operación de guardado)
        old_is_business_owner = getattr(instance, '__original_is_business_owner', None)

        # Si el valor de is_business_owner cambió
        if (created and instance.is_business_owner) or \
           (not created and old_is_business_owner != instance.is_business_owner):
            logger.info(f"CAMBIO DETECTADO para {instance.email}: is_business_owner cambió de '{old_is_business_owner}' a '{instance.is_business_owner}'. Sincronizando con Firebase...")
            update_firebase_custom_claim(instance.uid, instance.is_business_owner)
        else:
            logger.info(f"No hubo cambio significativo en is_business_owner para {instance.email}. No se necesita actualizar Firebase.")
    else:
        logger.warning(f"ADVERTENCIA: Usuario {instance.email} no tiene UID de Firebase. No se pudo sincronizar custom claim.")
