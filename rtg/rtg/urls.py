from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'gamebets', views.GameBetViewSet)
router.register(r'extras', views.ExtraViewSet)
router.register(r'extrabets', views.ExtraBetViewSet)

router.register(r'tournamentgroups', views.TournamentGroupViewSet)
router.register(r'tournamentrounds', views.TournamentRoundViewSet)
router.register(r'teams', views.TeamViewSet)
router.register(r'venues', views.VenueViewSet)
router.register(r'games', views.GameViewSet)

router.register(r'users', views.UserViewSet)
router.register(r'profiles', views.ProfileViewSet)
router.register(r'profiles_public', views.PublicProfileViewSet)
router.register(r'profiles_admin', views.AdminProfileViewSet)
router.register(r'posts', views.PostViewSet)
router.register(r'statistics', views.StatisticViewSet)

app_name = 'rtg'
urlpatterns = [
    url(r'^', include(router.urls, namespace='rtg')),
]
