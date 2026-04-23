from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView , SpectacularSwaggerView ,SpectacularRedocView


urlpatterns = [
    path('admin/', admin.site.urls),
 
    # API versiyasi v1
    path('api/auth/',include('apps.accounts.urls')),
    path('api/courses/',include('apps.courses.urls')),
    path('api/groups/',include('apps.groups.urls')),
    # path('api/attendance/',include('apps.attendance.urls')),
    # path('api/assignments/',include('apps.assignments.urls')),
    # path('api/results/',include('apps.results.urls')),
    # path('api/notifications/',include('apps.notifications.urls')),
    # path('api/messages/',include('apps.messages_app.urls')),
    # path('api/settings/',include('apps.settings_app.urls')),
    
    # Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
 