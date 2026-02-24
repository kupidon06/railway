from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('djengoo.urls', namespace='djengoo')),

    # API v1
    path('api/v1/', include([
        path('', include('apps.core.urls')),
        path('twin/', include('apps.twin.urls')),
        path('simulation/', include('apps.simulation.urls')),
        path('ai/', include('apps.ai.urls')),
        path('analytics/', include('apps.analytics.urls')),
        path('auth/token/', obtain_auth_token, name='api-token-auth'),
    ])),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
