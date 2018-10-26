from rest_framework import viewsets

from game.models import Game, Player, Ship, Turn
from game.serializers import (
    GameSerializer, PlayerSerializer, ShipSerializer, TurnSerializer)


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class ShipViewSet(viewsets.ModelViewSet):
    queryset = Ship.objects.all()
    serializer_class = ShipSerializer


class TurnViewSet(viewsets.ModelViewSet):
    queryset = Turn.objects.all()
    serializer_class = TurnSerializer
