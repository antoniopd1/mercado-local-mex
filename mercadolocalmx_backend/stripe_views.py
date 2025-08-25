# backend/mercadolocalmx_backend/stripe_views.py
from django.conf import settings
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging # Importar el módulo de logging
import stripe
from usuarios.models import CustomUser

# Crear una instancia de logger para este módulo
logger = logging.getLogger(__name__)

# La clave secreta se lee desde settings, que a su vez la obtiene de las variables de entorno.
stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateCheckoutSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            customer_id_to_use = user.stripe_customer_id

            # Verificar y crear el cliente de Stripe si no existe o si es inválido
            if not customer_id_to_use:
                try:
                    # Si el ID no existe en la base de datos, lo creamos
                    logger.info(f"Creando nuevo cliente de Stripe para el usuario: {user.id}")
                    customer = stripe.Customer.create(
                        email=user.email,
                        name=user.get_full_name() or user.username,
                        metadata={'django_user_id': user.id},
                    )
                    user.stripe_customer_id = customer.id
                    user.save()
                    customer_id_to_use = customer.id
                except stripe.error.StripeError as e:
                    logger.error(f"Error al crear el cliente de Stripe para el usuario {user.id}: {e}")
                    return Response({"error": "No se pudo crear el cliente de Stripe.", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    # Si el ID existe, intentamos verificarlo con Stripe
                    stripe.Customer.retrieve(customer_id_to_use)
                except stripe.error.InvalidRequestError:
                    # Si el ID es inválido, lo creamos de nuevo
                    logger.warning(f"ID de cliente de Stripe inválido para el usuario {user.id}. Creando uno nuevo.")
                    try:
                        customer = stripe.Customer.create(
                            email=user.email,
                            name=user.get_full_name() or user.username,
                            metadata={'django_user_id': user.id},
                        )
                        user.stripe_customer_id = customer.id
                        user.save()
                        customer_id_to_use = customer.id
                    except stripe.error.StripeError as e:
                        logger.error(f"Error al recrear el cliente de Stripe para el usuario {user.id}: {e}")
                        return Response({"error": "No se pudo crear el cliente de Stripe.", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            # Obtener el ID del plan de suscripción desde las configuraciones
            PRICE_ID = settings.STRIPE_MONTHLY_PLAN_PRICE_ID
            
            logger.info("Iniciando el proceso de creación de sesión de pago de Stripe.")
            checkout_session = stripe.checkout.Session.create(
                customer=customer_id_to_use,
                payment_method_types=['card'],
                line_items=[{
                    'price': PRICE_ID,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=settings.FRONTEND_DOMAIN + '/subscription/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=settings.FRONTEND_DOMAIN + '/subscription/canceled',
            )
            logger.info(f"Sesión de checkout de Stripe creada correctamente con ID: {checkout_session.id}")
            return Response({'sessionId': checkout_session.id})

        except stripe.error.StripeError as e:
            logger.error(f"Error fatal de Stripe: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error inesperado en la vista de checkout de Stripe: {e}")
            return Response({'error': 'Ocurrió un error inesperado.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
