from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views import index

urlpatterns = [
    path('',           index,                       name='index'),
    path('admin/',     admin.site.urls),
    path('api/auth/',  include('apps.users.urls')),
    path('api/timer/', include('apps.timer.urls')),
    path('api/stats/', include('apps.stats.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
