from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from rest_auth.views import PasswordResetConfirmView
from rest_auth.views import PasswordResetView

admin.autodiscover()

urlpatterns = patterns('',
    # enable Django admin interface:
    url(r'^admin/', include(admin.site.urls)),

    # APP: rtg
    url(r'^rtg/', include('rtg.urls', namespace='rtg')),

    # use django-rest-auth extension views for password reset endpoints
    url(r'^rest-auth/password/reset/$', PasswordResetView.as_view(), name='rest_password_reset'),
    url(r'^rest-auth/password/reset/confirm/$', PasswordResetConfirmView.as_view(), name='rest_password_reset_confirm'),
    # url(r'^password/change/$', PasswordChangeView.as_view(), name='rest_password_change'),

    # djangorestramework-jwt extension Authentication views
    url(r'^api-token-auth/', 'rest_framework_jwt.views.obtain_jwt_token'),
    url(r'^api-token-refresh/', 'rest_framework_jwt.views.refresh_jwt_token'),
    url(r'^api-token-verify/', 'rest_framework_jwt.views.verify_jwt_token'),

    # custom extensions for registering new users in the JWT context
    url(r'^api-token-register/', 'rtg.registration_overrides.rtg_register'),

    # contact form endpoint
    url(r'^contact/$', 'rtg.views.contact_request', name='rtg_contact_request'),
)

# Uncomment the next line to serve media files in dev.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += patterns('',
#                             url(r'^__debug__/', include(debug_toolbar.urls)),
#                             )
