# backend/mercadolocalmx_backend/stripe_webhook_views.py
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import ObjectDoesNotExist
import logging # Importar el módulo de logging
import stripe
import json

# Importar el modelo de usuario para las actualizaciones
from usuarios.models import CustomUser

# Crear una instancia de logger para este módulo
logger = logging.getLogger(__name__)

# La clave secreta se lee desde settings, que a su vez la obtiene de las variables de entorno.
stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def stripe_webhook(request):
    """
    Gestiona los eventos de webhook de Stripe para actualizar el estado de los usuarios.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        # Intenta construir el evento usando la firma para verificar su autenticidad.
        # Es CRUCIAL que el STRIPE_WEBHOOK_SECRET se guarde de forma segura en variables de entorno.
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Error de valor: Payload de webhook de Stripe inválido. Detalles: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Error de firma: Firma del webhook de Stripe inválida. Detalles: {e}")
        return HttpResponse(status=400)

    try:
        # Maneja el evento de suscripción completada
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            customer_id = session.get('customer')
            
            user = CustomUser.objects.get(stripe_customer_id=customer_id)
            user.is_business_owner = True
            user.has_active_subscription = True
            user.save()
            logger.info(f"Usuario {user.email} actualizado a business owner y con suscripción activa.")

        # Maneja la expiración o cancelación de la suscripción
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            customer_id = subscription.get('customer')
            
            user = CustomUser.objects.get(stripe_customer_id=customer_id)
            user.is_business_owner = False
            user.has_active_subscription = False
            user.save()
            logger.info(f"Suscripción de {user.email} finalizada. is_business_owner y has_active_subscription actualizados a False.")

    except ObjectDoesNotExist:
        # Manejo del caso donde el usuario no se encuentra
        customer_id_from_event = event['data']['object'].get('customer')
        logger.warning(f"Usuario no encontrado con stripe_customer_id: {customer_id_from_event}")
        return HttpResponse(status=404)
    except Exception as e:
        # Manejo de cualquier otro error inesperado durante la actualización del usuario
        logger.error(f"Error inesperado al actualizar el usuario en el webhook de Stripe: {e}")
        return HttpResponse(status=500)

    # El webhook de Stripe espera un status 200 para confirmar la recepción exitosa
    return HttpResponse(status=200)
