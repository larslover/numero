from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

# URL patterns for your project
urlpatterns = [
    # i18n URL for language selection
    path('i18n/', include('django.conf.urls.i18n')),

    # API routes — these should be accessible without language prefixes
    path('api/', include('shifts.urls')),  # Includes all API routes
]

# Adding i18n patterns for user-facing URLs
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),  # Admin routes
    path('', include('shifts.urls')),  # Your main views (e.g., schedule, login, etc.)
)
