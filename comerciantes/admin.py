# backend/comerciantes/admin.py

from django.contrib import admin
from .models import Business, Offer # Importa también Offer


# Personaliza la administración del modelo Business
@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la tabla de listado de negocios en el admin
    list_display = (
        'name', 
        'municipality', 
        'location_type', 
        'business_type', # NUEVO: Tipo de negocio
        'contact_phone', 
        'is_paid_member', # NUEVO: Miembro de pago
        'membership_expires_at', # NUEVO: Fecha de expiración de membresía
        'user', 
        'created_at'
    )
    
    # Campos por los que se puede filtrar la lista de negocios
    list_filter = (
        'municipality', 
        'location_type', 
        'business_type', # NUEVO: Tipo de negocio para filtrar
        'is_paid_member', # NUEVO: Filtro por estado de pago
    )
    
    # Campos por los que se puede buscar texto en la barra de búsqueda
    search_fields = (
        'name', 
        'what_they_sell', 
        'street_address', 
        'contact_phone',
        'social_media_facebook_username',
        'social_media_instagram_username',
        'social_media_twitter_username',
    )
    
    # Organización de los campos en el formulario de edición/creación de un negocio
    fieldsets = (
        (None, { # Grupo principal
            'fields': ('user', 'name', 'what_they_sell', 'hours')
        }),
        ('Ubicación y Contacto', {
            'fields': ('municipality', 'street_address', 'location_type', 'contact_phone')
        }),
        ('Redes Sociales e Imagen', {
            'fields': ('social_media_facebook_username', 'social_media_instagram_username', 'social_media_twitter_username', 'image_url')
        }),
        ('Clasificación y Membresía', { # NUEVO FIELDSET para los campos relacionados con el pago
            'fields': (
                'business_type',        # NUEVO: Tipo de negocio
                'is_paid_member',       # NUEVO: Estado de pago
                'membership_expires_at', # NUEVO: Fecha de expiración
                'last_payment_date'     # NUEVO: Última fecha de pago
            )
        }),
        ('Fechas del Registro', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',) # Esto hace que este grupo esté colapsado por defecto
        }),
    )
    
    # Campos que se mostrarán pero no se podrán editar
    readonly_fields = ('created_at', 'updated_at')

# Mantiene el registro del modelo Offer como lo tenías
admin.site.register(Offer)