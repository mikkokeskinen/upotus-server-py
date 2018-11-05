import rest_framework.urls
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from game import viewsets as game_viewsets

router = routers.DefaultRouter()
router.register(r'game', game_viewsets.GameViewSet, basename='game')
router.register(r'player', game_viewsets.PlayerViewSet, basename='player')
router.register(r'ship', game_viewsets.ShipViewSet, basename='ship')
router.register(r'turn', game_viewsets.TurnViewSet, basename='turn')

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api-auth/', include(rest_framework.urls))
]
