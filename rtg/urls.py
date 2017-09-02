from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from rest_auth.views import PasswordResetConfirmView
from rest_auth.views import PasswordResetView
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

from main.registration_overrides import rtg_register
from main.views import contact_request

admin.autodiscover()

urlpatterns = [
    # enable Django admin interface:
    url(r'^admin/', admin.site.urls),

    # APP: rtg
    url(r'^rtg/', include('main.urls')),

    # use django-rest-auth extension views for password reset endpoints
    url(r'^rest-auth/password/reset/$', PasswordResetView.as_view(), name='rest_password_reset'),
    url(r'^rest-auth/password/reset/confirm/$', PasswordResetConfirmView.as_view(), name='rest_password_reset_confirm'),
    # url(r'^password/change/$', PasswordChangeView.as_view(), name='rest_password_change'),

    # djangorestramework-jwt extension Authentication views
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),
    url(r'^api-token-verify/', verify_jwt_token),

    # custom extensions for registering new users in the JWT context
    url(r'^api-token-register/', rtg_register),

    # contact form endpoint
    url(r'^contact/$', contact_request, name='rtg_contact_request'),
]

# Uncomment the next line to serve media files in dev.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += patterns('',
#                             url(r'^__debug__/', include(debug_toolbar.urls)),
#                             )
