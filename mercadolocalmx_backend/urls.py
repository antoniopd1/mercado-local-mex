# backend/mercado_local_mx/urls.py

from django.contrib import admin
from django.urls import path, include
from comerciantes.urls import router as comerciantes_router
from .stripe_views import CreateCheckoutSessionView
from .stripe_webhook_views import stripe_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(comerciantes_router.urls)),

    path('api/create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('api/stripe-webhook/', stripe_webhook, name='stripe-webhook'),
]