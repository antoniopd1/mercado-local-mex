# usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin # Importa UserAdmin
from .models import CustomUser # Importa tu CustomUser

# Si quieres personalizar cómo se muestra CustomUser en el admin
class CustomUserAdmin(UserAdmin):
    # Asegúrate de que 'is_business_owner' esté en los fieldsets y/o list_display
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('uid', 'is_business_owner',)}), # Añade tus campos personalizados aquí
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('uid', 'is_business_owner',)}),
    )
    list_display = ('username', 'email', 'is_staff', 'is_business_owner') # Para verlo en la lista
    search_fields = ('username', 'email', 'uid') # Para poder buscar por ellos

admin.site.register(CustomUser, CustomUserAdmin)