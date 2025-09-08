# comerciantes/views.py
import logging
from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from django.contrib.auth import get_user_model
import django_filters.rest_framework

from .filters import OfferFilter, BusinessFilter
from .models import Business, Offer
from .serializers import BusinessSerializer, OfferSerializer
from .permissions import IsBusinessOwner, IsOwnerOfBusiness, IsOwnerOfOffer

from datetime import date

import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

User = get_user_model()

# Crea una instancia de logger para este módulo
logger = logging.getLogger(__name__)

class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    
    # Se habilita el backend de filtros de Django
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = BusinessFilter

    def get_permissions(self):
        # Esta lógica de permisos es excelente. Asigna permisos específicos
        # para cada tipo de acción, garantizando la seguridad en el acceso.
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'my_business':
            permission_classes = [permissions.IsAuthenticated, IsBusinessOwner]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsBusinessOwner, IsOwnerOfBusiness]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        # La lógica para filtrar negocios por suscripción es robusta y clara.
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return Business.objects.all()
        
        if self.action == 'my_business':
            if self.request.user.is_authenticated:
                return Business.objects.filter(user=self.request.user)
            return Business.objects.none()
        
        # Lógica para mostrar solo los negocios de usuarios con suscripción activa.
        if self.request.user.is_authenticated:
            return Business.objects.filter(user__is_business_owner=True)
        
        return Business.objects.none()

    def update(self, request, *args, **kwargs):
        # Sobreescribe el método update para agregar logs
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            
            # Agrega este log para ver si la petición está llegando
            logger.info(f"Intentando actualizar el negocio ID: {instance.id}. Datos recibidos.")
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            
            # Este es el punto crítico donde se intenta guardar el archivo en S3
            serializer.save()
            
            # Agrega este log si la subida fue exitosa
            logger.info(f"Negocio ID: {instance.id} actualizado exitosamente. El archivo debería estar en S3.")
            
            return Response(serializer.data)
        
        except Exception as e:
            # Agrega este log para capturar el error y la traza completa
            logger.error(f"Error fatal al actualizar el negocio ID: {instance.id}.", exc_info=True)
            return Response({"error": "Ocurrió un error interno."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        # Asocia el negocio con el usuario actual automáticamente al crearlo.
        serializer.save(user=self.request.user)
        
    @action(detail=False, methods=['get'])
    def my_business(self, request):
        user_business_qs = self.get_queryset()

        if user_business_qs.exists():
            serializer = self.get_serializer(user_business_qs.first())
            return Response(serializer.data)
        else:
            return Response({"detail": "No se encontró ningún negocio para este usuario."},
                            status=status.HTTP_404_NOT_FOUND)


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer

    filterset_class = OfferFilter
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]

    def get_permissions(self):
        # De nuevo, la lógica de permisos está correctamente definida por acción.
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'my_offers':
            permission_classes = [permissions.IsAuthenticated, IsBusinessOwner]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsBusinessOwner, IsOwnerOfOffer]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_authenticated and self.request.user.is_staff:
            return queryset
        
        if self.action == 'my_offers':
            if self.request.user.is_authenticated and self.request.user.is_business_owner:
                try:
                    user_business = Business.objects.get(user=self.request.user)
                    return queryset.filter(business=user_business)
                except Business.DoesNotExist:
                    return Offer.objects.none()
            return Offer.objects.none()
        
        if self.request.user.is_authenticated:
            if self.action == 'list':
                # Esta es una excelente implementación de la lógica de negocio para
                # mostrar solo ofertas activas de negocios con suscripción.
                return queryset.filter(
                    is_active=True,
                    end_date__gte=date.today(),
                    business__user__is_business_owner=True
                )
            elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
                return queryset
            
        return Offer.objects.none()

    def update(self, request, *args, **kwargs):
        # Agregamos la misma lógica de depuración al ViewSet de Ofertas
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            
            logger.info(f"Intentando actualizar la oferta ID: {instance.id}.")
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            logger.info(f"Oferta ID: {instance.id} actualizada exitosamente. El archivo debería estar en S3.")
            return Response(serializer.data)
        
        except Exception as e:
            logger.error(f"Error fatal al actualizar la oferta ID: {instance.id}.", exc_info=True)
            return Response({"error": "Ocurrió un error interno."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        try:
            # Asocia la oferta con el negocio del usuario actual.
            user_business = Business.objects.get(user=self.request.user)
        except Business.DoesNotExist:
            # Lanza una excepción clara si el usuario no tiene negocio.
            raise PermissionDenied("Debes tener un negocio registrado para crear ofertas.")
        serializer.save(business=user_business)

    @action(detail=False, methods=['get'])
    def my_offers(self, request):
        queryset = self.get_queryset()
        filtered_queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(filtered_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(filtered_queryset, many=True)
        return Response(serializer.data)