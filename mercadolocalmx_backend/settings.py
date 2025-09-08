"""
Django settings for mercadolocalmx_backend project.
"""

from pathlib import Path
import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials
import logging
import dj_database_url


# Crear una instancia de logger para este módulo
logger = logging.getLogger(__name__)

# Carga las variables de entorno del archivo .env si existe.
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent



# --- Variables de Entorno y Seguridad ---
# Las siguientes variables deben estar definidas en el entorno de producción.
SECRET_KEY = os.environ.get('SECRET_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
STRIPE_MONTHLY_PLAN_PRICE_ID = os.environ.get('STRIPE_MONTHLY_PLAN_PRICE_ID')
FRONTEND_DOMAIN = os.environ.get('FRONTEND_DOMAIN')

# Configuración de AWS S3
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
logger.info("Configuración de AWS S3")
print("Configuración de AWS S3")

# Configuración de django-storages
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_USE_SSL = True
AWS_QUERYSTRING_AUTH = False
logger.info("Configuración de django-storages")
print("Configuración de django-storages")

# Define la URL de tus archivos de medios
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
MEDIA_ROOT = ''
logger.info("Define la URL de tus archivos de medios")
print("Define la URL de tus archivos de medios")

# DEBUG: En producción, DEBE ser False.
# Evitar fallbacks para no habilitarlo por error en un entorno real.
DEBUG = os.environ.get('DEBUG') == 'True'

# ALLOWED_HOSTS: En producción, debe contener los dominios de tu sitio.
# No debe tener fallbacks en producción para evitar peticiones maliciosas.
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')


# --- RESTO DE LA CONFIGURACIÓN ---

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'comerciantes',
    'usuarios',
    'rest_framework',
    'corsheaders',
    'django_filters',
    'storages', # Añadir si se usa django-storages para archivos de medios
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise debe ir justo después de SecurityMiddleware para ser efectivo.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS: En producción, usa CORS_ALLOWED_ORIGINS con una lista.
CORS_ALLOW_ALL_ORIGINS = True
#CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'mercadolocalmx_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mercadolocalmx_backend.wsgi.application'


# Database
# Ahora se lee de variables de entorno. Se recomienda no tener fallbacks
# en producción para evitar errores de conexión con credenciales no deseadas.
DATABASES = {
    'default': dj_database_url.config(
        # Lee la URL de la variable de entorno DATABASE_URL
        default=os.environ.get('DATABASE_URL')
    )
}

# Configuración de Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'mercadolocalmx_backend.authentication.FirebaseAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ]
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Configuración para que Whitenoise comprima y optimice los archivos estáticos.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'usuarios.CustomUser'


# Obtiene la variable de entorno de las credenciales de Firebase
firebase_creds_source = os.environ.get('FIREBASE_ADMIN_SDK_CREDENTIALS')


# Inicializar Firebase Admin SDK si no está inicializado
if not firebase_admin._apps and firebase_creds_source:
    try:
        # Intenta inicializar usando una ruta de archivo (para desarrollo)
        if os.path.exists(firebase_creds_source):
            cred = credentials.Certificate(firebase_creds_source)
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK inicializado desde archivo de credenciales 1.")
            logger.info("Firebase Admin SDK inicializado desde archivo de credenciales.")
        
        # Si no es una ruta de archivo, intenta inicializarlo desde una cadena JSON (para producción)
        else:
            # Parseamos la cadena JSON de la variable de entorno
            creds_json = json.loads(firebase_creds_source)
            cred = credentials.Certificate(creds_json)
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK inicializado desde cadena JSON.")
            logger.info("Firebase Admin SDK inicializado desde cadena JSON.")

    except Exception as e:
        print(f"Error fatal al inicializar Firebase Admin SDK: {e}")
        logger.critical(f"Error fatal al inicializar Firebase Admin SDK: {e}")

