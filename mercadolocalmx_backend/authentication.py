# mercadolocalmx_backend/authentication.py

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from firebase_admin import auth, exceptions as firebase_exceptions
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class FirebaseAuthentication(BaseAuthentication):
    """
    Autenticación de Django REST Framework usando tokens ID de Firebase.
    """
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')

        if not auth_header:
            return None

        parts = auth_header.split()
        if parts[0].lower() != 'bearer' or len(parts) == 1 or len(parts) > 2:
            raise AuthenticationFailed('Formato de cabecera de autorización inválido. Se esperaba "Bearer <token>".')

        id_token = parts[1]

        try:
            # Usa leeway=5. Puedes subirlo a 10 o 15 si persisten los problemas de "Token used too early"
            decoded_token = auth.verify_id_token(id_token, check_revoked=True,clock_skew_seconds=10)
        except firebase_exceptions.FirebaseError as e:
            logger.error(f"Fallo en la verificación del token de Firebase: {e}")
            if "Token used too early" in str(e):
                raise AuthenticationFailed('Error de autenticación: El token es demasiado nuevo. Por favor, inicia sesión de nuevo.')
            raise AuthenticationFailed('Token ID de Firebase inválido o expirado.')
        except Exception as e:
            logger.error(f"Error inesperado durante la verificación del token de Firebase: {e}")
            raise AuthenticationFailed('Ocurrió un error inesperado durante la autenticación.')

        firebase_uid = decoded_token['uid']
        email = decoded_token.get('email')

        try:
            user = User.objects.get(uid=firebase_uid)
        except User.DoesNotExist:
            try:
                user = User.objects.create_user(
                    username=firebase_uid,
                    email=email,
                    uid=firebase_uid
                )
                logger.info(f"Nuevo usuario de Django creado para Firebase UID: {firebase_uid}")
            except Exception as e:
                logger.error(f"Error al crear el usuario de Django para Firebase UID {firebase_uid}: {e}")
                raise AuthenticationFailed(f"No se pudo crear el usuario de Django: {e}")
        except Exception as e:
            logger.error(f"Error inesperado al buscar/crear usuario de Django: {e}")
            raise AuthenticationFailed(f"Error al procesar el usuario de Django: {e}")

        return (user, None)