from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # for language switching
]

# Add admin + app URLs to the i18n_patterns so they respect LANGUAGE_CODE
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('shifts.urls')),
)
