from django.urls import include, re_path
from rest_framework.routers import DefaultRouter

from main import views

router = DefaultRouter()
router.register(r'bets', views.BetViewSet)
router.register(r'bettables', views.BettableViewSet)

router.register(r'tournamentgroups', views.TournamentGroupViewSet)
router.register(r'tournamentrounds', views.TournamentRoundViewSet)
router.register(r'teams', views.TeamViewSet)
router.register(r'venues', views.VenueViewSet)
router.register(r'games', views.GameViewSet)
router.register(r'game-kickoffs', views.GameKickoffsViewSet)
router.register(r'extras', views.ExtraViewSet)

router.register(r'users', views.UserViewSet)
router.register(r'users_public', views.PublicUserViewSet, 'users_public')
router.register(r'users_admin', views.AdminUserViewSet, 'users_admin')
router.register(r'posts', views.PostViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'statistics', views.StatisticViewSet)

app_name = 'rtg'
urlpatterns = [
    re_path(r'^', include((router.urls, 'rtg'), 'rtg')),
]
