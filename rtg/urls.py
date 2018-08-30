from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin
from rest_auth.views import PasswordResetConfirmView, PasswordChangeView
from rest_auth.views import PasswordResetView
from rest_framework_jwt.views import refresh_jwt_token, verify_jwt_token

from main.login_overrides import rtg_obtain_jwt_token
from main.registration_overrides import rtg_register
from main.views import contact_request, health

admin.autodiscover()

urlpatterns = [
    # enable Django admin interface:
    path('admin/', admin.site.urls),

    # APP: main
    path('rtg/', include('main.urls')),

    # use django-rest-auth extension views for password reset endpoints
    path('rest-auth/password/reset/', PasswordResetView.as_view(), name='rest_password_reset'),
    path('rest-auth/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='rest_password_reset_confirm'),
    path('rest-auth/password/change/', PasswordChangeView.as_view(), name='rest_password_change'),

    # djangorestramework-jwt extension Authentication views
    path('api-token-auth/', rtg_obtain_jwt_token),
    path('api-token-refresh/', refresh_jwt_token),
    path('api-token-verify/', verify_jwt_token),

    # custom extensions for registering new users in the JWT context
    path('api-token-register/', rtg_register),

    # contact form endpoint
    path('contact/', contact_request, name='rtg_contact_request'),

    path('healthcheck/', health)
]

# Uncomment the next line to serve media files in dev.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
