# backend/comerciantes/urls.py

# Añade path e include, aunque no se usen directamente aquí, es buena práctica
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessViewSet, OfferViewSet

router = DefaultRouter()
router.register(r'businesses', BusinessViewSet) # URL: /api/businesses/
# CORRECCIÓN: Añade 'basename' para OfferViewSet
router.register(r'offers', OfferViewSet, basename='offer') # URL: /api/offers/, con basename explícito

# Cuando incluyes este router en tu urls.py principal,
# las rutas serán, por ejemplo: /api/businesses/, /api/offers/
urlpatterns = router.urls