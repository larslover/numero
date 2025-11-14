from django.urls import path, include
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from shifts.views.schedule import service_worker

urlpatterns = [
    path('service-worker.js', service_worker, name="service-worker"),  # REQUIRED
    path('api/', include('shifts.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('shifts.urls')),
)
