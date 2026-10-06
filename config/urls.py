from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView , SpectacularSwaggerView ,SpectacularRedocView


def setup_superadmin(request):
    try:
        from django.contrib.auth import get_user_model
        from django.core.management import call_command
        import io

        out = io.StringIO()
        call_command('migrate', stdout=out, interactive=False)
        migrate_output = out.getvalue()

        User = get_user_model()
        created_users = []
        for username in ['Ibrohim99', 'ibrohim99']:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'full_name': 'Ibrohim Abduraximov',
                    'role': 'admin',
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True,
                }
            )
            user.set_password('ibrohim_0919')
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.role = 'admin'
            user.save()
            created_users.append(username)

        return JsonResponse({
            'status': 'success',
            'message': 'SuperAdmin muvaffaqiyatli yaratildi!',
            'users': created_users,
            'migrate_log': migrate_output
        })
    except Exception as e:
        import traceback
        return JsonResponse({'status': 'error', 'error': str(e), 'trace': traceback.format_exc()}, status=500)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('setup-superadmin-init/', setup_superadmin),

    # API versiyasi v1
    path('api/auth/', include('apps.accounts.urls')),
    path('api/courses/', include('apps.courses.urls')),
    path('api/groups/', include('apps.groups.urls')),
    path('api/attendance/', include('apps.attendance.urls')),
    path('api/assignments/', include('apps.assignments.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/messages/', include('apps.messages_app.urls')),
    path('api/results/', include('apps.results.urls')),

    # Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)