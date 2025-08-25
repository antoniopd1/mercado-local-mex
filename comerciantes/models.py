# comerciantes/models.py

from django.db import models
from django.conf import settings # Para settings.AUTH_USER_MODEL
from decimal import Decimal
from datetime import date, timedelta # Importa 'date' y 'timedelta' para defaults de fecha

def default_end_date():
    return date.today() + timedelta(days=7)

# --- OPCIONAL: Definición de Choices para campos específicos ---
# Se recomienda usar choices para estandarizar entradas de datos
# Puedes mover esto a un archivo 'choices.py' si se vuelve muy largo.

# --- Opciones para el campo 'municipality' ---
MUNICIPALITY_CHOICES = [
    ('ABASOLO', 'Abasolo'),
    ('ACAMBARO', 'Acámbaro'),
    ('ALLENDE', 'San Miguel de Allende'),
    ('APASEO_EL_ALTO', 'Apaseo el Alto'),
    ('APASEO_EL_GRANDE', 'Apaseo el Grande'),
    ('ATARJEA', 'Atarjea'),
    ('CELAYA', 'Celaya'),
    ('MANUEL_DOBLADO', 'Manuel Doblado'),
    ('COMONFORT', 'Comonfort'),
    ('CORONEO', 'Coroneo'),
    ('CORTAZAR', 'Cortazar'),
    ('CUERAMARO', 'Cuerámaro'),
    ('DOCTOR_MORA', 'Doctor Mora'),
    ('DOLORES_HIDALGO', 'Dolores Hidalgo Cuna de la Independencia Nacional'),
    ('GUANAJUATO', 'Guanajuato'),
    ('HUANIMARO', 'Huanímaro'),
    ('IRAPUATO', 'Irapuato'),
    ('JARAL_DEL_PROGRESO', 'Jaral del Progreso'),
    ('JERECUARO', 'Jerécuaro'),
    ('LEON', 'León'),
    ('MOROLEON', 'Moroleón'),
    ('OCAMPO', 'Ocampo'),
    ('OJITOS_DE_JAUREGUI', 'Ojo de Agua de Latillas'), # Unidades Territoriales o comunidades
    ('PENJAMO', 'Pénjamo'),
    ('PUEBLO_NUEVO', 'Pueblo Nuevo'),
    ('PURISIMA_DEL_RINCON', 'Purísima del Rincón'),
    ('ROMITA', 'Romita'),
    ('SALAMANCA', 'Salamanca'),
    ('SALVATIERRA', 'Salvatierra'),
    ('SAN_DIEGO_DE_LA_UNION', 'San Diego de la Unión'),
    ('SAN_FELIPE', 'San Felipe'),
    ('SAN_FRANCISCO_DEL_RINCON', 'San Francisco del Rincón'),
    ('SAN_JOSE_ITURBIDE', 'San José Iturbide'),
    ('SAN_LUIS_DE_LA_PAZ', 'San Luis de la Paz'),
    ('SANTA_CATARINA', 'Santa Catarina'),
    ('SANTA_CRUZ_DE_JUVENTINO_ROSAS', 'Santa Cruz de Juventino Rosas'),
    ('SANTIAGO_MARAVATIO', 'Santiago Maravatío'),
    ('SILAO', 'Silao de la Victoria'),
    ('TARANDACUAO', 'Tarandacuao'),
    ('TARIMORO', 'Tarimoro'),
    ('TIERRA_BLANCA', 'Tierra Blanca'),
    ('URIANGATO', 'Uriangato'),
    ('VALLE_DE_SANTIAGO', 'Valle de Santiago'),
    ('VICTORIA', 'Victoria'),
    ('VILLAGRAN', 'Villagrán'),
    ('XICHU', 'Xichú'),
    ('YURIRIA', 'Yuriria'),
]

# --- Opciones para el campo 'location_type' ---
LOCATION_TYPE_CHOICES = [
    ('PLAZA_TEXTIL', 'Plaza Textil'),
    ('TIANGUIS', 'Tianguis'),
    ('MERCADO', 'Mercado'),
    ('LOCAL_CALLE', 'Local a la Calle'),
    ('ONLINE', 'Solo Online (sin ubicación física)'),
    ('OTRO', 'Otro'),
]

# --- Opciones para el campo 'business_type' ---
BUSINESS_TYPE_CHOICES = [
    # El primer valor en cada tupla debe ser el que espera el backend
    # y el segundo es el texto que se muestra.
    # El valor vacío del frontend ('') no se mapea directamente en CHOICES de Django,
    # sino que se maneja como un campo opcional o con un default.
    ('ROPA_MAYOREO_MENUDEO', 'Tiendas de Ropa al Mayoreo/Menudeo'),
    ('TALLERES_CONFECCION', 'Talleres de Confección'),
    ('TELAS_INSUMOS', 'Tiendas de Telas e Insumos Textiles'),
    ('MERCERIAS', 'Mercerías'),
    ('CALZADO', 'Calzado'),
    ('ABARROTES', 'Abarrotes'),
    ('TORTILLERIAS', 'Tortillerías'),
    ('CARNICERIAS', 'Carnicerías'),
    ('FRUTERIAS_VERDULERIAS', 'Fruterías y Verdulerías'),
    ('PANADERIAS', 'Panaderías'),
    ('FONDAS_COCINAS', 'Fondas/Cocinas Económicas'),
    ('TAQUERIAS_ANTOJITOS', 'Taquerías/Antojitos'),
    ('ESTETICAS', 'Estéticas'),
    ('PELUQUERIAS_BARBERIAS', 'Peluquerías/Barberías'),
    ('FARMACIAS', 'Farmacias'),
    ('PAPELERIAS_CIBER', 'Papelerías/Ciber-cafés'),
    ('TLAPALERIAS_FERRETERIAS', 'Tlapalerías/Ferreterías'),
    ('REFACCIONARIAS', 'Refaccionarias'),
    ('TALLERES_MECANICOS', 'Talleres Mecánicos'),
    ('VULCANIZADORAS', 'Vulcanizadoras'),
    ('VETERINARIAS', 'Veterinarias'),
    ('FLORISTERIAS', 'Floristerías'),
    ('JOYERIAS', 'Joyerías'),
    ('TIENDAS_REGALOS', 'Tiendas de Regalos'),
    ('LAVANDERIAS', 'Lavanderías'),
    ('MUEBLERIAS', 'Mueblerías'),
    ('TIENDAS_ELECTRONICA', 'Tiendas de Electrónica'),
    ('DULCERIAS', 'Dulcerías'),
    ('AGENCIAS_VIAJES', 'Agencias de Viajes'),
    ('ZAPATERIAS', 'Zapaterías'),
    ('ARTESANIAS', 'Artesanías y Productos Típicos'),
    ('SERVICIOS_GENERALES', 'Servicios Generales (ej. reparaciones, cerrajería)'),
    ('PRODUCTOS_VARIOS', 'Productos Varios / Chácharas'),
    ('OTROS', 'Otros'),
]

# ---------------------------------------------------------------

class Business(models.Model):
    """
    Modelo para representar un negocio o comerciante registrado en la plataforma.
    """
    # Relación con el modelo de usuario personalizado.
    # Usar settings.AUTH_USER_MODEL es la práctica recomendada.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='business_profile',
        help_text="Usuario asociado a este negocio."
    )
    
    name = models.CharField(
        max_length=200,
        help_text="Nombre oficial o comercial del negocio."
    )
    what_they_sell = models.TextField(
        help_text="Descripción de los productos o servicios que ofrece el negocio."
    )
    hours = models.CharField(
        max_length=255,
        help_text="Horario de atención del negocio (ej. 'Lun-Vie: 9am-6pm')."
    )
    municipality = models.CharField(
        max_length=100,
        choices=MUNICIPALITY_CHOICES, # Opcional: Usar choices definidos arriba
        help_text="Municipio donde se encuentra el negocio."
    )
    street_address = models.CharField(
        max_length=255,
        help_text="Dirección física completa del negocio."
    )
    location_type = models.CharField(
        max_length=50,
        choices=LOCATION_TYPE_CHOICES, # Opcional: Usar choices definidos arriba
        help_text="Tipo de ubicación del negocio (ej. Tienda Física, Online, Puesto)."
    )
    contact_phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Número de teléfono de contacto del negocio (opcional)."
    )
    social_media_facebook_username = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Nombre de usuario de Facebook (opcional)."
    )
    social_media_instagram_username = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Nombre de usuario de Instagram (opcional)."
    )
    social_media_tiktok_username = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Nombre de usuario de TikTok (opcional)."
    )
    logo = models.ImageField(
        upload_to='business_logos/', 
        blank=True, 
        null=True,
        help_text="Logotipo del negocio."
    )
    business_type = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, # Si decides usar choices y quieres que sea obligatorio, quita null=True, blank=True
        choices=BUSINESS_TYPE_CHOICES, # Opcional: Usar choices definidos arriba
        help_text="Categoría o tipo de negocio (ej. Restaurante, Ropa, Servicios)."
    )

    # Campos de membresía
    is_paid_member = models.BooleanField(
        default=False,
        help_text="Indica si el negocio es un miembro de pago."
    )
    membership_expires_at = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="Fecha y hora de expiración de la membresía."
    )
    last_payment_date = models.DateField(
        blank=True, 
        null=True,
        help_text="Fecha del último pago de la membresía."
    )

    # Timestamps automáticos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Negocio"
        verbose_name_plural = "Negocios" # Buena práctica para los nombres en plural
        ordering = ['name'] # Ordenar negocios por nombre por defecto

    def __str__(self):
        return self.name



class Offer(models.Model):
    """
    Modelo para representar una oferta o promoción publicada por un negocio.
    """
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='offers', # Permite acceder a las ofertas desde un negocio: `business_instance.offers.all()`
        help_text="El negocio que publica esta oferta."
    )
    title = models.CharField(
        max_length=200,
        help_text="Título breve y atractivo de la oferta (ej. 'Descuento 20% en pizzas')."
    )
    description = models.TextField(
        help_text="Descripción detallada de la oferta, incluyendo qué se ofrece, condiciones, etc."
    )
    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'), # Default a 0.00 si no se especifica
        null=True,               # Permite que el campo sea NULL en la base de datos
        blank=True,              # Permite que el campo esté vacío en formularios
        help_text="Precio original del producto/servicio antes de aplicar el descuento (opcional)."
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'), # Default a 0.00 si no se especifica
        help_text="Precio con descuento o precio final de la oferta."
    )
    
    # Campo para la imagen de la oferta
    image = models.ImageField(
        upload_to='offers_images/', # Carpeta donde se guardarán las imágenes de ofertas
        null=True,
        blank=True,
        help_text="Imagen representativa de la oferta (opcional)."
    )

    # Fechas de validez de la oferta
    start_date = models.DateField(
        default=date.today, # Por defecto, la fecha de inicio es hoy
        help_text="Fecha a partir de la cual la oferta es válida."
    )
    end_date = models.DateField(
        default=default_end_date , # Por defecto, la oferta dura 7 días desde hoy
        help_text="Fecha hasta la cual la oferta es válida."
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Indica si la oferta está activa y visible para los usuarios."
    )

    # Timestamps automáticos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Oferta"
        verbose_name_plural = "Ofertas"
        ordering = ['-created_at'] # Ordenar ofertas por fecha de creación descendente

    def __str__(self):
        # Muestra el título de la oferta y el nombre del negocio asociado
        return f"{self.title} ({self.business.name})"