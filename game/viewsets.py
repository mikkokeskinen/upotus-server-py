from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from game.models import Game, Player, Ship, Turn
from game.permissions import IsPlayer, IsOwner
from game.serializers import (
    GameSerializer, PlayerSerializer, ShipSerializer, TurnSerializer)


class GameViewSet(viewsets.ModelViewSet):
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated, IsPlayer]

    def get_queryset(self, *args, **kwargs):
        return Game.objects.filter(players__user=self.request.user).distinct()

    def perform_create(self, serializer):
        super().perform_create(serializer)

        Player.objects.create(
            game=serializer.instance,
            user=self.request.user,
        )


class PlayerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class ShipViewSet(viewsets.ModelViewSet):
    queryset = Ship.objects.all()
    serializer_class = ShipSerializer


class TurnViewSet(viewsets.ModelViewSet):
    queryset = Turn.objects.all()
    serializer_class = TurnSerializer
