from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include
from django.contrib import admin
from .views import redirect_to_spanish  # Importamos la vista de redirección

urlpatterns = [
    path('', redirect_to_spanish),  # Redirige la raíz a `/es/`
    path('i18n/', include('django.conf.urls.i18n')),  # URL para cambiar el idioma
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('home.urls')),  # Incluye las URLs de la app `home`
    path('ckeditor5/', include('django_ckeditor_5.urls')),
)
