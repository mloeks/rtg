from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenRefreshView

from main.login_overrides import RtgObtainJSONWebToken
from main.registration_overrides import rtg_register
from main.views import contact_request, health

admin.autodiscover()

urlpatterns = [
    # enable Django admin interface:
    path('admin/', admin.site.urls),

    # APP: main
    path('rtg/', include('main.urls')),

    # use dj-rest-auth extension views for password reset endpoints
    path('rest-auth/', include('dj_rest_auth.urls')),
    # make dj-rest-auth reset url generation work - it requires a view named 'password_reset_confirm',
    # note that we don't make use of the URL returned here, but having a view with uid and token parameters is
    # required. See default_url_generator in dj_rest_auth.forms & FAQ of dj-rest-auth docs.
    path('passwordreset/<uid>/<token>/', TemplateView.as_view(), name='password_reset_confirm'),

    # djangorestramework_simplejwt extension Authentication views
    path('api-token-auth/', RtgObtainJSONWebToken.as_view()),
    path('api-token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # custom extensions for registering new users in the JWT context
    # TODO P2 can we override dj-rest-auth's RegisterSerializer directly instead, bypassing the view and configure REGISTER_SERIALIZER?
    path('api-token-register/', rtg_register),

    # contact form endpoint
    path('contact/', contact_request, name='rtg_contact_request'),

    path('healthcheck/', health)
]

# Uncomment the next line to serve media files in dev.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
