from rest_framework import serializers
from .models import Business, Offer # Correct import for serializers to use models

class BusinessSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.uid') # Asumiendo que quieres el UID de Firebase

    class Meta:
        model = Business
        fields = '__all__'
        read_only_fields = [
            'user',
            'is_paid_member',
            'membership_expires_at',
            'last_payment_date',
            'created_at',
            'updated_at',
        ]

class OfferSerializer(serializers.ModelSerializer):
    # ¡CAMBIO CLAVE AQUÍ!
    # Definimos 'business' para que use el BusinessSerializer.
    # 'read_only=True' es apropiado si la relación de negocio es establecida por la vista
    # (ej., un comerciante solo puede crear ofertas para su propio negocio),
    # y solo queremos mostrar los detalles del negocio, no permitir su edición a través de la oferta.
    business = BusinessSerializer(read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'business', 'title', 'description', 'original_price',
            'discount_price', 'image', 'start_date', 'end_date', 'is_active',
            'created_at', 'updated_at'
        ]
        # ¡CAMBIO CLAVE AQUÍ!
        # Removemos 'business' de read_only_fields en el Meta.
        # Ya que lo hemos definido explícitamente arriba para ser serializado como un objeto,
        # no queremos que DRF lo trate solo como un ID read-only para la salida.
        read_only_fields = ['id', 'created_at', 'updated_at']