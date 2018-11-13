from django.db import transaction
from django.db.models import Max
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

    def perform_create(self, serializer):
        max_number = Turn.objects.filter(
            player=serializer.validated_data['player']).aggregate(
            Max('number'))['number__max']
        if not max_number:
            max_number = 0
        # TODO: possible race condition
        serializer.validated_data['number'] = max_number + 1
        serializer.save()

        # TODO: hit and sink_ship
