from django.urls import path, include
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from shifts.views.schedule import service_worker

urlpatterns = [
    # Language switcher (stays outside)
    path('i18n/', include('django.conf.urls.i18n')),

    # API routes (no translation needed)
    path('api/', include('shifts.urls')),
]

# All normal site pages + service worker MUST be inside i18n_patterns
urlpatterns += i18n_patterns(
    path('service-worker.js', service_worker, name="service-worker"),
    path('admin/', admin.site.urls),
    path('', include('shifts.urls')),
)
