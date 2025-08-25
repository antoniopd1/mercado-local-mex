# comerciantes/permissions.py
from rest_framework import permissions

class IsBusinessOwner(permissions.BasePermission):
    """
    Permiso personalizado para permitir el acceso solo a usuarios que son dueños de negocio.
    Este permiso es a nivel de VISTA (has_permission) y se usa para controlar
    el acceso a operaciones de CREACIÓN y LISTADO, y como requisito base para las demás.
    """
    message = 'Debes ser un dueño de negocio para realizar esta acción. Por favor, asegúrate de tener una suscripción activa.'

    def has_permission(self, request, view):
        # Este permiso verifica si el usuario autenticado tiene el atributo is_business_owner en True.
        return request.user and request.user.is_authenticated and request.user.is_business_owner


class IsOwnerOfBusiness(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo a los propietarios de objetos
    Business editarlos o eliminarlos. Este permiso es a nivel de OBJETO (has_object_permission).
    """
    message = 'No tienes permiso para realizar esta acción en este negocio.' # Mensaje de error personalizado

    def has_object_permission(self, request, view, obj):
        # Los permisos de lectura (GET, HEAD, OPTIONS) están permitidos para cualquier solicitud SAFE_METHODS.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Los permisos de escritura (PUT, PATCH, DELETE) solo se otorgan al propietario del negocio.
        # 'obj.user' es el campo correcto que enlaza el negocio al usuario.
        return obj.user == request.user


class IsOwnerOfOffer(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo a los propietarios del negocio
    manipular sus propias ofertas. Este permiso es a nivel de OBJETO (has_object_permission).
    """
    message = 'No tienes permiso para realizar esta acción en esta oferta.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 'obj.business.user' es la cadena correcta para el dueño del negocio de la oferta.
        return obj.business.user == request.user