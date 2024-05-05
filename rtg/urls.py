from dj_rest_auth.views import PasswordResetConfirmView, PasswordChangeView
from dj_rest_auth.views import PasswordResetView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from main.login_overrides import RtgObtainJSONWebToken
from main.registration_overrides import rtg_register
from main.views import contact_request, health
from rest_framework_simplejwt.views import TokenRefreshView

admin.autodiscover()

urlpatterns = [
    # enable Django admin interface:
    path('admin/', admin.site.urls),

    # APP: main
    path('rtg/', include('main.urls')),

    # use dj-rest-auth extension views for password reset endpoints
    path('rest-auth/password/reset/', PasswordResetView.as_view(), name='rest_password_reset'),
    path('rest-auth/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='rest_password_reset_confirm'),
    path('rest-auth/password/change/', PasswordChangeView.as_view(), name='rest_password_change'),

    # djangorestramework_simplejwt extension Authentication views
    path('api-token-auth/', RtgObtainJSONWebToken.as_view()),
    path('api-token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # custom extensions for registering new users in the JWT context
    path('api-token-register/', rtg_register),

    # contact form endpoint
    path('contact/', contact_request, name='rtg_contact_request'),

    path('healthcheck/', health)
]

# Uncomment the next line to serve media files in dev.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
