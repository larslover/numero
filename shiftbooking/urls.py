from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/', include('shifts.urls')),

]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path("admin/", include("shifts.urls")), 
    path('', include('shifts.urls')),
   

)
