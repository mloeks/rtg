import json
import logging

from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.decorators import parser_classes
from rest_framework.filters import OrderingFilter, DjangoFilterBackend
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.parsers import MultiPartParser

from main import filters as rtgfilters
from . import permissions as rtg_permissions
from .forms import RtgContactForm
from .serializers import *

LOG = logging.getLogger('rtg.' + __name__)


class BetViewSet(viewsets.ModelViewSet):
    queryset = Bet.objects.all()
    serializer_class = BetSerializer

    permission_classes = (rtg_permissions.IsAdminOrOwner,)

    # return all bets of the user and all other bets if deadline has passed
    filter_backends = (rtgfilters.IsOwnerOrDeadlinePassed, OrderingFilter, DjangoFilterBackend)
    filter_fields = ('bettable',)

    # never use pagination for bets, since they should never be displayed paginated to the user in the UI
    pagination_class = None

    ordering_fields = ('id', 'bettable')
    ordering = ('id',)

    def perform_create(self, serializer):
        """ Always set the Bet user to the current user. """
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """ Always set the Bet user to the current user. """
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """
            Optionally restricts the returned bets to a given user or game,
            by filtering against query parameters in the URL.
        """
        queryset = Bet.objects.all()
        user_id = self.request.query_params.get('user_id', None)
        bettable_id = self.request.query_params.get('bettable_id', None)
        if user_id is not None:
            queryset = queryset.filter(user__pk=user_id)
        if bettable_id is not None:
            queryset = queryset.filter(bettable__pk=bettable_id)
        return queryset


class BettableViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bettable.objects.all()
    serializer_class = BettableSerializer
    pagination_class = None

    filter_backends = (OrderingFilter, rtgfilters.GamesWithBetsOpenIfParamSet)

    ordering_fields = ('id', 'deadline')
    ordering = ('deadline',)


class ExtraViewSet(viewsets.ModelViewSet):
    queryset = Extra.objects.all()
    serializer_class = ExtraSerializer
    permission_classes = (rtg_permissions.IsAdminOrAuthenticatedReadOnly,)
    pagination_class = None


class TournamentGroupViewSet(viewsets.ModelViewSet):
    queryset = TournamentGroup.objects.all()
    serializer_class = TournamentGroupSerializer
    permission_classes = (rtg_permissions.IsAdminOrAuthenticatedReadOnly,)
    pagination_class = None


class TournamentRoundViewSet(viewsets.ModelViewSet):
    queryset = TournamentRound.objects.all()
    serializer_class = TournamentRoundSerializer
    permission_classes = (rtg_permissions.IsAdminOrAuthenticatedReadOnly,)
    pagination_class = None


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = (rtg_permissions.IsAdminOrAuthenticatedReadOnly,)
    pagination_class = None
    filter_backends = (OrderingFilter,)

    ordering_fields = ('id', 'name', 'abbreviation')
    ordering = ('name',)


class VenueViewSet(viewsets.ModelViewSet):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    permission_classes = (rtg_permissions.IsAdminOrAuthenticatedReadOnly,)
    pagination_class = None


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = (rtg_permissions.IsAdminOrAuthenticatedReadOnly,)
    pagination_class = None

    filter_backends = (OrderingFilter, rtgfilters.GamesWithBetsOpenIfParamSet)

    ordering_fields = ('id', 'kickoff', 'deadline', 'venue', 'round')
    ordering = ('kickoff',)


# TODO may be needed for avatar upload
# @parser_classes((JSONParser, FormParser, MultiPartParser,))
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (rtg_permissions.UserPermissions,)
    pagination_class = None

    filter_backends = (OrderingFilter,)
    ordering = ('first_name', 'last_name', 'username',)

    def get_queryset(self):
        """
            Restricts the returned users to the requesting user only, if he is not admin.
            This is necessary because the LIST request cannot be globally restricted to admins (then the user cannot
            even request its own instance)
        """
        queryset = User.objects.all()
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(pk=user.pk)
        return queryset


# how the public can see users
class PublicUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = PublicUserSerializer
    pagination_class = None


# how admin users can see all users
class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = (rtg_permissions.IsAdmin,)
    pagination_class = None


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (rtg_permissions.IsAdminOrAuthenticatedReadOnly,)

    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filter_fields = ('news_appear',)
    ordering = ('-date_created',)


class StatisticViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Statistic.objects.all()
    serializer_class = StatisticSerializer
    pagination_class = None

    filter_backends = (rtgfilters.RelatedOrderingFilter,)
    ordering = ('-points', '-no_volltreffer', 'user__username')


################## CONTACT FORM endpoint

# TODO this should be moved into a separate app, not into the RTG REST API
# TODO why does CORS_WHITELIST not work and @csrf_exempt is necessary?
@csrf_exempt
def contact_request(request):
    if request.method == 'POST' and request.is_ajax():
        form = RtgContactForm(request.POST)
        if form.is_valid():
            payload = {
                'author': form.cleaned_data['author'],
                'email': form.cleaned_data['email'],
                'content': form.cleaned_data['content']
            }

            subject = '%sDeine Nachricht an die RTG 2016' % settings.EMAIL_PREFIX
            message = render_to_string('rtg/contact_copy.txt', {'contact_request': payload})
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [payload['email']])

            subject = '%sKontaktaufnahme von %s' % (settings.EMAIL_PREFIX, payload['author'],)
            message = payload['content']
            send_mail(subject, message, payload['email'], [settings.DEFAULT_STAFF_EMAIL])

            return HttpResponse('OK')
        else:
            return HttpResponseBadRequest(json.dumps(form.errors))
    else:
        raise PermissionDenied()
