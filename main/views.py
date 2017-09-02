import json

from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, filters
from rest_framework.decorators import parser_classes
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.parsers import MultiPartParser

from main import filters as rtgfilters
from . import permissions as rtg_permissions
from .forms import RtgContactForm
from .serializers import *


class GameBetViewSet(viewsets.ModelViewSet):
    queryset = GameBet.objects.all()
    serializer_class = GameBetSerializer

    permission_classes = (rtg_permissions.IsAdminOrOwner,)

    # return all bets of the user and all other bets if game deadline has passed
    filter_backends = (rtgfilters.IsOwnerOrGameDeadlinePassed, filters.OrderingFilter)

    # never use pagination for bets, since they should never be displayed paginated to the user in the UI
    pagination_class = None

    ordering_fields = ('id', 'game')
    ordering = ('id',)

    def perform_create(self, serializer):
        """ Always set the GameBet user to the current user. """
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """ Always set the GameBet user to the current user. """
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """
            Optionally restricts the returned gamebets to a given user or game,
            by filtering against query parameters in the URL.
        """
        queryset = GameBet.objects.all()
        user_id = self.request.query_params.get('user_id', None)
        game_id = self.request.query_params.get('game_id', None)
        if user_id is not None:
            queryset = queryset.filter(user__pk=user_id)
        if game_id is not None:
            queryset = queryset.filter(game__pk=game_id)
        return queryset


class ExtraViewSet(viewsets.ModelViewSet):
    queryset = Extra.objects.all()
    serializer_class = ExtraSerializer
    permission_classes = (rtg_permissions.IsAdminOrAuthenticatedReadOnly,)
    pagination_class = None


class ExtraBetViewSet(viewsets.ModelViewSet):
    queryset = ExtraBet.objects.all()
    serializer_class = ExtraBetSerializer

    permission_classes = (rtg_permissions.IsAdminOrOwner,)

    # return all bets of the user and all other bets if game deadline has passed
    filter_backends = (rtgfilters.IsOwnerOrExtraDeadlinePassed, filters.OrderingFilter)

    # never use pagination for bets, since they should never be displayed paginated to the user in the UI
    pagination_class = None

    ordering_fields = ('id', 'extra')
    ordering = ('id',)

    def perform_create(self, serializer):
        """ Always set the GameBet user to the current user. """
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """ Always set the GameBet user to the current user. """
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """
            Optionally restricts the returned extrabets to a given user,
            by filtering against a `user_id` query parameter in the URL.
        """
        queryset = ExtraBet.objects.all()
        user_id = self.request.query_params.get('user_id', None)
        if user_id is not None:
            queryset = queryset.filter(user__pk=user_id)
        return queryset


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
    filter_backends = (filters.OrderingFilter,)

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

    filter_backends = (filters.OrderingFilter, rtgfilters.GamesWithBetsOpenIfParamSet)

    ordering_fields = ('id', 'kickoff', 'deadline', 'venue', 'round')
    ordering = ('kickoff',)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # TODO does not work as expected yet. cf. failing test
    permission_classes = (rtg_permissions.UserPermissions,)

    pagination_class = None

    filter_backends = (filters.OrderingFilter,)
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


@parser_classes((JSONParser, FormParser, MultiPartParser,))
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (rtg_permissions.ProfilePermissions,)
    pagination_class = None

    def get_queryset(self):
        """
            cf. UserViewSet
        """
        queryset = Profile.objects.all()
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(user__pk=user.pk)
        return queryset


class PublicProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = PublicProfileSerializer
    pagination_class = None


class AdminProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = AdminProfileSerializer
    permission_classes = (rtg_permissions.IsAdmin,)
    pagination_class = None


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (rtg_permissions.IsAdminOrAuthenticatedReadOnly,)

    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter,)
    filter_fields = ('news_appear',)
    ordering = ('-date_created',)


class StatisticViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Statistic.objects.all()
    serializer_class = StatisticSerializer
    pagination_class = None

    filter_backends = (rtgfilters.RelatedOrderingFilter,)
    ordering = ('-points', '-no_volltreffer', 'user__username')


################## CONTACT FORM endpoint. Should go into a separate app, not into RTG REST API

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