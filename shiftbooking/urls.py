from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),

    # ✅ Include your API routes OUTSIDE i18n_patterns
    path('api/', include('shifts.api_urls')),
]

# 🌐 Language-prefixed URLs (used only for views needing translation)
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('shifts.urls')),
)
