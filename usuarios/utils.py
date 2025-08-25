# usuarios/utils.py
import firebase_admin
from firebase_admin import auth
import logging

logger = logging.getLogger(__name__)

def update_firebase_custom_claim(user_uid, is_owner_status):
    """
    Actualiza el custom claim 'isBusinessOwner' en Firebase para un usuario dado.
    Esto invalidará el token actual del usuario, forzando un refresco
    para obtener el nuevo claim.
    """
    try:
        # Obtén los claims actuales del usuario
        user = auth.get_user(user_uid)
        current_claims = user.custom_claims if user.custom_claims else {}

        # Actualiza el claim 'isBusinessOwner'
        current_claims['isBusinessOwner'] = is_owner_status

        # Establece los nuevos claims para el usuario en Firebase
        auth.set_custom_user_claims(user_uid, current_claims)

        # Opcional: Revocar tokens para forzar al frontend a obtener uno nuevo más rápido
        auth.revoke_refresh_tokens(user_uid) 
        logger.info(f"Custom claim 'isBusinessOwner' para {user_uid} actualizado a {is_owner_status}.")

    except Exception as e:
        logger.error(f"Error al actualizar custom claim para {user_uid}: {e}")
